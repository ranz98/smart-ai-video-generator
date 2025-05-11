import os
import random # Keep if used elsewhere, otherwise can remove
import ffmpeg
import multiprocessing # Keep if used elsewhere, otherwise can remove
from PIL import Image # Import Pillow for image processing

def get_duration(file_path):
    """
    Uses ffmpeg to get the duration of a media file.
    Returns duration in seconds or 0 on error.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found for duration check: {file_path}")
        return 0

    try:
        # Use ffprobe to get duration
        # Removed capture_stderr=True as it's not a valid option for ffmpeg.probe()
        probe = ffmpeg.probe(file_path, v='error', select_streams='a:0', show_entries='format=duration')
        duration = float(probe['format']['duration'])
        return duration
    except ffmpeg.Error as e:
        # FFmpeg errors during probe will be captured by the Python exception handling
        print(f"FFmpeg Error getting duration for {file_path}: {e.stderr.decode()}")
        return 0
    except Exception as e:
        print(f"Unexpected error getting duration for {file_path}: {e}")
        return 0



def create_video_from_ordered_images(image_paths, audio_path, output_path, fps=24):
    """
    Creates a video from a specific ordered list of image file paths,
    matching the length of the audio. Uses ffmpeg pipe for efficiency.

    Args:
        image_paths (list): An ordered list of full paths to image files.
        audio_path (str): The full path to the audio file.
        output_path (str): The full path where the output video should be saved.
        fps (int): Frames per second for the output video (default is 24).

    Returns:
        bool: True if video was created successfully, False otherwise.
    """
    num_images = len(image_paths)
    if not image_paths:
        print("No image paths provided for video creation.")
        return False # Indicate failure

    if not os.path.exists(audio_path):
        print(f"Audio file not found at: {audio_path}")
        return False # Indicate failure


    audio_duration = get_duration(audio_path)
    if audio_duration <= 0:
        print(f"Could not get valid duration for audio file: {audio_path}")
        return False # Indicate failure

    # Calculate the display duration for each image
    # Ensure duration is positive to avoid errors
    image_display_duration = audio_duration / num_images if num_images > 0 else 0.1

    if image_display_duration <= 0:
        print("Calculated image display duration is zero or negative.")
        return False # Indicate failure


    print(f"Creating video from {num_images} images and audio ({audio_duration:.2f}s). Each image: {image_display_duration:.2f}s")

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)


    try:
        # Define the input stream for images using pipe
        # Use pix_fmt='rgb24' because PIL reads images as RGB by default
        # Setting framerate=1/image_display_duration directly in input is more precise
        input_video = ffmpeg.input('pipe:', format='image2pipe', pix_fmt='rgb24', framerate=1/image_display_duration)
        input_audio = ffmpeg.input(audio_path)

        # --- DEBUG PRINTS: Check types before calling ffmpeg.output ---
        print(f"DEBUG: Type of input_video: {type(input_video)}")
        print(f"DEBUG: Type of input_audio: {type(input_audio)}")
        print(f"DEBUG: Is input_video None? {input_video is None}")
        print(f"DEBUG: Is input_audio None? {input_audio is None}")
        # -------------------------------------------------------------


        # Define the output stream
        # CORRECTED: Pass input streams as separate positional arguments
        process = ffmpeg.output(
            input_video, # Pass input_video directly
            input_audio, # Pass input_audio directly
            output_path,
            # FFmpeg global options (often placed before output file)
            # These are positional arguments
            '-preset', 'medium', # Encoding speed vs compression efficiency ('fast', 'medium', 'slow')
            '-crf', '23', # Constant Rate Factor (lower is higher quality, 23 is a good default)
            '-max_muxing_queue_size', '1024', # Increase queue size for pipe input
            '-shortest', '1', # Ensure video ends with the shortest stream (audio) - explicitly set
            # Output stream specific options (often placed after output file, before map/codec options)
            # These are keyword arguments
            vcodec='libx264', # H.264 codec
            pix_fmt='yuv420p', # Standard pixel format for compatibility
            r=fps, # Output frame rate
            acodec='aac', # AAC audio codec
            strict='experimental', # Needed for some codecs/features
        ).run_async(pipe_stdin=True, overwrite_output=True, capture_stderr=True) # Run asynchronously and pipe stdin, capture stderr


        # Pipe image data to stdin in the specified order
        for i, img_path in enumerate(image_paths):
            if not os.path.exists(img_path):
                print(f"Warning: Image file not found at {img_path}, skipping.")
                # Skipping might cause sync issues. A better approach might be to use a placeholder image.
                continue # Skip this image

            try:
                # Open image using PIL to ensure consistent RGB format for piping
                with Image.open(img_path) as img:
                    # Convert to RGB if not already
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    # Write raw image data to the pipe
                    # Ensure image is closed after processing
                    # PIL image objects don't strictly need explicit close in 'with' block, but harmless
                    # img.close()
                    process.stdin.write(img.tobytes())
            except Exception as e:
                print(f"Error processing image {img_path} for piping: {e}")
                continue # Skip this image

        process.stdin.close() # Close the stdin pipe
        stdout, stderr = process.communicate() # Wait for the process to finish and get output

        # Check if the output file was successfully created and is not empty
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"Video '{output_path}' created successfully.")
            return True # Indicate success
        else:
            print(f"Video creation failed or resulted in an empty file: {output_path}")
            # Print ffmpeg stderr output for more details
            if stderr:
                 print(f"FFmpeg stderr:\n{stderr.decode()}")
            return False # Indicate failure

    except ffmpeg.Error as e:
        print(f"FFmpeg Error creating video: {e.stderr.decode()}")
        return False # Indicate failure
    except Exception as e:
        print(f"An unexpected error occurred during video creation: {e}")
        return False # Indicate failure


# Keep these functions as they might be useful independently,
# but they won't be called directly by the Flask route we are setting up.
def remove_silence(input_file, output_file, silence_thresh=-30, min_silence_len=0.1):
    """
    Remove silence from an audio file using ffmpeg's silenceremove filter.

    Args:
        input_file (str): Full path to the input audio file.
        output_file (str): Full path where the silence-removed audio should be saved.
        silence_thresh (int): Silence threshold in dB (default -30).
        min_silence_len (float): Minimum silence duration in seconds (default 0.1).

    Returns:
        bool: True if silence removal was successful, False otherwise.
    """
    if not os.path.exists(input_file):
        print(f"Error: Input audio file not found for silence removal: {input_file}")
        return False

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    try:
        print(f"Removing silence from {input_file}...")
        # Run ffmpeg to detect and remove silence
        # Add -y for overwrite without prompt, capture_stderr for debugging
        ffmpeg.input(input_file).output(output_file, af=f"silenceremove=start_periods=1:start_threshold={silence_thresh}dB:start_duration={min_silence_len}s").run(overwrite_output=True, capture_stderr=True)
        print(f"Silence removed, file saved as {output_file}")
        # Verify output file exists and is not empty
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
             return True
        else:
             print(f"Silence removal failed or resulted in an empty file: {output_file}")
             return False

    except ffmpeg.Error as e:
        # Print ffmpeg stderr output for debugging
        print(f"An error occurred while removing silence: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during silence removal: {e}")
        return False


def speed_up_audio(input_file, output_file, speed_factor=1.20):
    """
    Speed up the audio by a given factor using ffmpeg's atempo filter.

    Args:
        input_file (str): Full path to the input audio file.
        output_file (str): Full path where the sped-up audio should be saved.
        speed_factor (float): The factor by which to speed up the audio (default 1.20).

    Returns:
        bool: True if audio speed up was successful, False otherwise.
    """
    if not os.path.exists(input_file):
        print(f"Error: Input audio file not found for speed up: {input_file}")
        return False

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    try:
        print(f"Speeding up audio from {input_file} by {speed_factor}x...")
        # Run ffmpeg to speed up the audio
        # Add -y for overwrite without prompt, capture_stderr for debugging
        # Note: atempo filter only supports values between 0.5 and 100.
        # Chaining multiple atempo filters is needed for factors outside this range.
        # For simplicity, assuming speed_factor is within the valid range.
        if not (0.5 <= speed_factor <= 100):
             print(f"Warning: Speed factor {speed_factor} is outside the valid range for atempo (0.5-100). Using 1.0.")
             speed_factor = 1.0 # Default to no speed up if factor is invalid

        ffmpeg.input(input_file).output(output_file, af=f"atempo={speed_factor}").run(overwrite_output=True, capture_stderr=True)
        print(f"Audio sped up by {speed_factor}x, file saved as {output_file}")
        # Verify output file exists and is not empty
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
             return True
        else:
             print(f"Audio speed up failed or resulted in an empty file: {output_file}")
             return False

    except ffmpeg.Error as e:
        # Print ffmpeg stderr output for debugging
        print(f"An error occurred while speeding up the audio: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during audio speed up: {e}")
        return False


# Removed process_images_and_audio and main functions as they are not needed for Flask integration
