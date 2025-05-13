import os
import random # Included as per user's allowed imports, not used in this script.
import ffmpeg
import multiprocessing # Included as per user's allowed imports, not used in this script.
import tempfile
import sys
from datetime import datetime # Import the datetime module

# Define the base path for the output folder
BASE_OUTPUT_FOLDER = r"D:\Program Files\xampp\htdocs\shorts\output"

def create_video_from_images_and_mp3(prefix: str, speed_multiplier_str: str = "1.0"):
    """
    Creates an MP4 video from image files and an MP3 audio file found in a
    dynamically determined folder (based on the current date and BASE_OUTPUT_FOLDER),
    filtering files by a given prefix and adjusting playback speed.
    Each image is displayed for an equal duration, and the total video length
    matches the MP3's original duration divided by the speed multiplier.

    Args:
        prefix (str): The prefix that image and MP3 file names must start with.
                      E.g., if files are 'Gen87046_image.png' and 'Gen87046_audio.mp3',
                      the prefix would be 'Gen87046'.
        speed_multiplier_str (str): A string representing the speed multiplier (e.g., "1.2").
                                    A value greater than 1.0 speeds up the video; less than 1.0 slows it down.
    """
    image_files = []
    mp3_file = None

    # Determine folder_path based on the current date
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(BASE_OUTPUT_FOLDER, current_date_str)

    # Check if the dynamically determined folder exists
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found at '{folder_path}'. Please ensure it exists or is created.")
        sys.exit(1)

    try:
        speed_multiplier = float(speed_multiplier_str)
        if speed_multiplier <= 0:
            raise ValueError("Speed multiplier must be a positive number.")
    except ValueError as e:
        print(f"Error: Invalid speed multiplier '{speed_multiplier_str}'. {e}")
        sys.exit(1)

    # Output video name includes the prefix and formatted speed multiplier
    output_video_name = f"{prefix}_speed{speed_multiplier_str.replace('.', '_')}_output.mp4"

    # Step 1: Identify all relevant image files and the MP3 file based on the prefix
    print(f"Scanning folder: '{folder_path}' for files starting with prefix '{prefix}'")
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.startswith(prefix):
            ext = file_name.lower().split('.')[-1]
            # List of common image formats
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff']:
                image_files.append(file_path)
            elif ext == 'mp3':
                if mp3_file is None:
                    mp3_file = file_path  # Take the first MP3 file found for this prefix
                else:
                    print(f"Warning: Multiple MP3 files found for prefix '{prefix}'. Using '{os.path.basename(mp3_file)}'.")

    # Step 2: Validate found files for the given prefix
    if not image_files:
        print(f"Error: No images found starting with prefix '{prefix}' in '{folder_path}'.")
        sys.exit(1)

    if mp3_file is None:
        print(f"Error: No MP3 file found starting with prefix '{prefix}' in '{folder_path}'.")
        sys.exit(1)

    # Sort images to ensure a consistent (alphabetical) order in the video
    image_files.sort()

    print(f"\nFound {len(image_files)} images for prefix '{prefix}':")
    for img_path in image_files:
        print(f"  - {os.path.basename(img_path)}")
    print(f"Using MP3: '{os.path.basename(mp3_file)}'")

    # Step 3: Get the original duration of the MP3 file
    original_mp3_duration = 0.0
    try:
        probe = ffmpeg.probe(mp3_file)
        original_mp3_duration = float(probe['format']['duration'])
        print(f"\nOriginal MP3 duration: {original_mp3_duration:.2f} seconds")
    except ffmpeg.Error as e:
        print(f"Error probing MP3 file: {e.stderr.decode()}")
        sys.exit(1)
    except KeyError:
        print("Error: Could not determine MP3 duration. Missing 'duration' in probe output.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while probing MP3: {e}")
        sys.exit(1)

    if original_mp3_duration <= 0:
        print("Error: MP3 duration is zero or negative. Cannot create video.")
        sys.exit(1)

    # Calculate the effective output duration based on the speed multiplier
    effective_output_duration = original_mp3_duration / speed_multiplier
    print(f"Target output video duration (sped up/down): {effective_output_duration:.2f} seconds")

    # Step 4: Calculate the display duration for each image based on the effective duration
    images_count = len(image_files)
    image_display_duration = effective_output_duration / images_count

    # Define a minimum duration per image to prevent very short or problematic slides
    min_single_image_duration = 0.04  # Approx. 25 frames per second (1/25)
    if image_display_duration < min_single_image_duration:
        print(f"Warning: Calculated image display duration is very low ({image_display_duration:.4f}s). "
              f"Consider fewer images or a longer original MP3/lower speed multiplier. Setting minimum to {min_single_image_duration}s per image.")
        image_display_duration = min_single_image_duration
        # If we force a minimum, the total video from images might become slightly longer than the effective duration.
        # This is fine as it will be trimmed by the 't' parameter during output.

    print(f"Each image will be displayed for {image_display_duration:.4f} seconds (before speed filter applied by FFmpeg).")

    output_video_path = os.path.join(folder_path, output_video_name)
    temp_list_file_path = None

    try:
        # Step 5: Create a temporary text file for FFmpeg's concat demuxer
        # This method allows specifying the duration for each image file in sequence.
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_list_file:
            temp_list_file_path = temp_list_file.name
            for img_path in image_files:
                # FFmpeg paths should use forward slashes even on Windows
                temp_list_file.write(f"file '{img_path.replace(os.sep, '/')}'\n")
                temp_list_file.write(f"duration {image_display_duration}\n")
            # A common quirk of the concat demuxer is that the last duration
            # might not be fully applied unless the last file is listed again.
            temp_list_file.write(f"file '{image_files[-1].replace(os.sep, '/')}'\n")

        print(f"\nCreated temporary image list file: {temp_list_file_path}")

        # Step 6: Construct and execute the FFmpeg command using ffmpeg-python
        # Input streams
        image_input_stream = ffmpeg.input(temp_list_file_path, format='concat', safe=0)
        audio_input_stream = ffmpeg.input(mp3_file)

        # Apply video speed filter (setpts)
        # 'setpts=1/SPEED_MULTIPLIER*PTS' speeds up the video.
        video_stream = image_input_stream.video.setpts(f'1/{speed_multiplier}*PTS')

        # Apply audio speed filter (atempo)
        # The 'atempo' filter changes the playback tempo of the audio without altering pitch.
        # It supports values between 0.5 and 2.0. For values outside this range,
        # we chain multiple atempo filters.
        audio_stream = audio_input_stream.audio
        current_speed_factor = speed_multiplier

        # Chain atempo filters for speeds > 2.0
        while current_speed_factor > 2.0:
            audio_stream = audio_stream.filter('atempo', 2.0)
            current_speed_factor /= 2.0
        # Chain atempo filters for speeds < 0.5
        while current_speed_factor < 0.5:
            audio_stream = audio_stream.filter('atempo', 0.5)
            current_speed_factor /= 0.5

        # Apply the remaining speed factor if it's not 1.0
        if current_speed_factor != 1.0:
            audio_stream = audio_stream.filter('atempo', current_speed_factor)


        # Output video configuration
        # 't=effective_output_duration' ensures the output video duration matches the calculated target.
        # 'vcodec', 'acodec', and 'pix_fmt' are set for broad compatibility.
        # 'r=30' sets the output framerate to 30 frames per second.
        (
            ffmpeg
            .output(video_stream, audio_stream, output_video_path,
                    vcodec='libx264',        # Video codec: H.264
                    acodec='aac',            # Audio codec: AAC
                    pix_fmt='yuv420p',       # Pixel format for compatibility
                    t=effective_output_duration, # Set output duration to effective_output_duration
                    r=30                     # Output framerate
                    )
            .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        )
        print(f"\nSuccessfully created video: {output_video_path}")

    except ffmpeg.Error as e:
        print(f"\nFFmpeg error during video creation:")
        print(f"Stdout: {e.stdout.decode()}")
        print(f"Stderr: {e.stderr.decode()}")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        # Step 7: Clean up the temporary list file
        if temp_list_file_path and os.path.exists(temp_list_file_path):
            os.remove(temp_list_file_path)
            print(f"\nCleaned up temporary file: {temp_list_file_path}")

# Main execution block
if __name__ == "__main__":
    # The prefix for the files you want to process
    example_prefix = "Gen87046"

    # The speed multiplier.
    # "1.0" for original speed.
    # "1.2" for 20% faster.
    # "0.8" for 20% slower.
    example_speed = "1.2"

    # Call the function with the prefix and desired speed.
    # The folder path will be determined automatically based on the current date.
    create_video_from_images_and_mp3(example_prefix, example_speed)