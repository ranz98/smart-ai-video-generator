import os
import random
import ffmpeg
import multiprocessing
import tempfile
import sys
from datetime import datetime

# Use a raw string for Windows path or double backslashes
BASE_OUTPUT_FOLDER = r"D:\Program Files\xampp\htdocs\shorts\output"

# Helper function to extract the sequence number for sorting
def extract_sequence_key(file_path):
    """
    Extracts the sequence number from a filename like '..._X-Y.ext'.
    Returns an integer for sorting or float('inf') if the pattern is not found.
    """
    base_name = os.path.basename(file_path)
    name_without_ext = os.path.splitext(base_name)[0] # e.g., Gen22972_21teo6_1-0
    try:
        # Split by the last underscore to isolate the part with the sequence number
        parts = name_without_ext.split('_')
        if len(parts) > 1:
            # The sequence part is assumed to be the last part, e.g., "1-0"
            sequence_indicator = parts[-1]
            # Split this part by '-' and take the first element as the number
            sequence_num_str = sequence_indicator.split('-')[0]
            return int(sequence_num_str)
        else:
            # If no underscore, or format is not as expected, treat as unsequenceable
            print(f"Warning: Could not parse sequence number from '{base_name}'. Will be sorted alphabetically/last.")
            return float('inf') # Places it at the end after numerically sorted items
    except (IndexError, ValueError):
        # If splitting fails or conversion to int fails
        print(f"Warning: Could not parse sequence number from '{base_name}'. Will be sorted alphabetically/last.")
        return float('inf') # Places it at the end

def create_videox(prefix: str, speed_multiplier_str: str = "1.0"):
    """
    Creates an MP4 video from image files and an MP3 audio file found in a
    dynamically determined folder (based on the current date and BASE_OUTPUT_FOLDER),
    filtering files by a given prefix and adjusting playback speed.
    Images are sorted based on a sequence number in their filenames (e.g., _1-0, _2-0).
    Each image is displayed for an equal duration, and the total video length
    matches the MP3's original duration divided by the speed multiplier.

    Args:
        prefix (str): The prefix that image and MP3 file names must start with.
        speed_multiplier_str (str): A string representing the speed multiplier.

    Returns:
        str: The full path to the created video file on success.
        False: If video creation fails due to missing files or FFmpeg errors.
    """
    image_files = []
    mp3_file = None

    current_date_str = datetime.now().strftime("%Y-%m-%d")
    folder_path = os.path.join(BASE_OUTPUT_FOLDER, current_date_str)

    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found at '{folder_path}'. Please ensure it exists or is created.")
        # sys.exit(1) # Avoid sys.exit in library function
        return False # Indicate failure

    try:
        speed_multiplier = float(speed_multiplier_str)
        if speed_multiplier <= 0:
            raise ValueError("Speed multiplier must be a positive number.")
    except ValueError as e:
        print(f"Error: Invalid speed multiplier '{speed_multiplier_str}'. {e}")
        # sys.exit(1) # Avoid sys.exit
        return False # Indicate failure

    output_video_name = f"{prefix}_speed{speed_multiplier_str.replace('.', '_')}_output.mp4"
    output_video_path = os.path.join(folder_path, output_video_name)

    print(f"Scanning folder: '{folder_path}' for files starting with prefix '{prefix}'")
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.startswith(prefix):
            ext = file_name.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff']:
                image_files.append(file_path)
            elif ext == 'mp3':
                if mp3_file is None:
                    mp3_file = file_path
                else:
                    print(f"Warning: Multiple MP3 files found for prefix '{prefix}'. Using '{os.path.basename(mp3_file)}'.")

    if not image_files:
        print(f"Error: No images found starting with prefix '{prefix}' in '{folder_path}'.")
        # sys.exit(1) # Avoid sys.exit
        return False # Indicate failure

    if mp3_file is None:
        print(f"Error: No MP3 file found starting with prefix '{prefix}' in '{folder_path}'.")
        # sys.exit(1) # Avoid sys.exit
        return False # Indicate failure

    # Sort images using the custom key to ensure correct numerical sequence
    image_files.sort(key=extract_sequence_key)

    print(f"\nFound {len(image_files)} images for prefix '{prefix}' (sorted by sequence number):")
    for img_path in image_files:
        print(f"  - {os.path.basename(img_path)}")
    print(f"Using MP3: '{os.path.basename(mp3_file)}'")

    original_mp3_duration = 0.0
    try:
        probe = ffmpeg.probe(mp3_file)
        original_mp3_duration = float(probe['format']['duration'])
        print(f"\nOriginal MP3 duration: {original_mp3_duration:.2f} seconds")
    except ffmpeg.Error as e:
        print(f"Error probing MP3 file: {e.stderr.decode()}")
        # sys.exit(1) # Avoid sys.exit
        return False # Indicate failure
    except KeyError:
        print("Error: Could not determine MP3 duration. Missing 'duration' in probe output.")
        # sys.exit(1) # Avoid sys.exit
        return False # Indicate failure
    except Exception as e:
        print(f"An unexpected error occurred while probing MP3: {e}")
        # sys.exit(1) # Avoid sys.exit
        return False # Indicate failure


    if original_mp3_duration <= 0:
        print("Error: MP3 duration is zero or negative. Cannot create video.")
        return False # Indicate failure

    effective_output_duration = original_mp3_duration / speed_multiplier
    print(f"Target output video duration (sped up/down): {effective_output_duration:.2f} seconds")

    images_count = len(image_files)
    image_display_duration = effective_output_duration / images_count

    min_single_image_duration = 0.04
    if image_display_duration < min_single_image_duration:
        print(f"Warning: Calculated image display duration is very low ({image_display_duration:.4f}s). "
              f"Consider fewer images or a longer original MP3/lower speed multiplier. Setting minimum to {min_single_image_duration}s per image.")
        image_display_duration = min_single_image_duration

    print(f"Each image will be displayed for {image_display_duration:.4f} seconds (before speed filter applied by FFmpeg).")

    temp_list_file_path = None

    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_list_file:
            temp_list_file_path = temp_list_file.name
            for img_path in image_files:
                temp_list_file.write(f"file '{img_path.replace(os.sep, '/')}'\n")
                temp_list_file.write(f"duration {image_display_duration}\n")
            # Add the last image again without duration to ensure the last frame is included for the remainder of the duration
            temp_list_file.write(f"file '{image_files[-1].replace(os.sep, '/')}'\n")


        print(f"\nCreated temporary image list file: {temp_list_file_path}")

        image_input_stream = ffmpeg.input(temp_list_file_path, format='concat', safe=0)
        audio_input_stream = ffmpeg.input(mp3_file)

        video_stream = image_input_stream.video.setpts(f'1/{speed_multiplier}*PTS')

        # Apply atempo filters iteratively to handle speed multipliers outside [0.5, 2.0] range
        audio_stream = audio_input_stream.audio
        current_speed_factor = speed_multiplier

        while current_speed_factor > 2.0:
            audio_stream = audio_stream.filter('atempo', 2.0)
            current_speed_factor /= 2.0
        while current_speed_factor < 0.5:
            audio_stream = audio_stream.filter('atempo', 0.5)
            current_speed_factor /= 0.5

        if current_speed_factor != 1.0:
            audio_stream = audio_stream.filter('atempo', current_speed_factor)


        (
            ffmpeg
            .output(video_stream, audio_stream, output_video_path,
                    vcodec='libx264',
                    acodec='aac',
                    pix_fmt='yuv420p', # Standard pixel format for broad compatibility
                    t=effective_output_duration, # Set the output duration based on the sped-up audio
                    r=30 # Set frame rate (e.g., 30 fps)
                    )
            .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
        )
        print(f"\nSuccessfully created video: {output_video_path}")
        return output_video_path # Return the path on success

    except ffmpeg.Error as e:
        print(f"\nFFmpeg error during video creation:")
        print(f"Stdout: {e.stdout.decode()}")
        print(f"Stderr: {e.stderr.decode()}")
        # sys.exit(1) # Avoid sys.exit
        return False # Indicate failure
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        # sys.exit(1) # Avoid sys.exit
        return False # Indicate failure
    finally:
        if temp_list_file_path and os.path.exists(temp_list_file_path):
            os.remove(temp_list_file_path)
            print(f"\nCleaned up temporary file: {temp_list_file_path}")


# Main execution block for testing (will not run when imported)
if __name__ == "__main__":
    # Example usage (replace with actual prefix and speed)
    # Make sure you have a dated folder inside BASE_OUTPUT_FOLDER
    # and place images like 'Gen12345_abc_1-0.png', 'Gen12345_def_2-0.png', ...
    # and an audio file like 'Gen12345_audio.mp3' in that dated folder.
    # Ensure FFmpeg is installed and in your system PATH.
    # Example: python video_creator.py Gen12345 1.0

    if len(sys.argv) > 2:
        example_prefix = sys.argv[1]
        example_speed = sys.argv[2]
        print(f"Running video_creator.py with prefix: {example_prefix}, speed: {example_speed}")
        created_video_path = create_videox(example_prefix, example_speed)

        if created_video_path:
            print(f"\nVideo creation successful. Output file: {created_video_path}")
        else:
            print("\nVideo creation failed.")

    else:
        print("Usage: python video_creator.py <prefix> <speed_multiplier>")
        print("Example: python video_creator.py Gen12345 1.2")
        # Optional: uncomment below to create dummy files for basic structure testing (FFmpeg will still fail without real media)
        # print("\nCreating dummy files for example test...")
        # example_prefix = "Gen99999"
        # today_date_str = datetime.now().strftime("%Y-%m-%d")
        # test_folder = os.path.join(BASE_OUTPUT_FOLDER, today_date_str)
        # os.makedirs(test_folder, exist_ok=True)
        # dummy_files_to_create = [
        #     f"{example_prefix}_abc_1-0.png",
        #     f"{example_prefix}_def_2-0.png",
        #     f"{example_prefix}_ghi_3-0.png",
        #     f"{example_prefix}_audio.mp3"
        # ]
        # for fname in dummy_files_to_create:
        #     with open(os.path.join(test_folder, fname), 'w') as f:
        #          f.write("dummy content")
        # print(f"Created dummy files in {test_folder}. NOTE: FFmpeg will likely fail with dummy content.")
        # print("\nRun with real files using: python video_creator.py Gen99999 1.0")Video creation response