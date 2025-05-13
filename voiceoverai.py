import os
import re
from datetime import datetime
from elevenlabs.client import ElevenLabs
from elevenlabs import save, play # Keep play if you use it elsewhere, otherwise can remove

# --- Configuration ---
# Define the base directory where dated subfolders will be created
BASE_SAVE_DIRECTORY = r'D:\Program Files\xampp\htdocs\shorts\output'
API_KEY_FILE_PATH = r'E:\elevenlabsapi.txt' # Path to your ElevenLabs API key file

# Load API key
api_key_E = None
try:
    with open(API_KEY_FILE_PATH, 'r') as file:
        api_key_E = file.read().strip()
    if not api_key_E:
        raise ValueError("ElevenLabs API key is empty.")
    print("ElevenLabs API key loaded successfully.")
except FileNotFoundError:
    print(f"Error: ElevenLabs API key file not found at {API_KEY_FILE_PATH}")
except Exception as e:
    print(f"Error loading ElevenLabs API key: {e}")

# Initialize ElevenLabs client
clientE = None
if api_key_E:
    try:
        clientE = ElevenLabs(api_key=api_key_E)
        # Optional: Test a simple call to verify the key/client
        # clientE.voices.get_all()
        print("ElevenLabs client initialized successfully.")
    except Exception as e:
        print(f"Error initializing ElevenLabs client: {e}")
        clientE = None


def fetch_voiceover(script, original_save_path_from_app):
    """
    Generates voiceover for the given script using ElevenLabs API
    and saves the audio to a date-specific subfolder within BASE_SAVE_DIRECTORY.

    Args:
        script (str): The text script to convert to speech.
        original_save_path_from_app (str):
            The original save path suggestion from app.py (e.g., "my_video/audio.mp3" or just "audio.mp3").
            Only the filename component of this path will be used. The directory
            will be determined by BASE_SAVE_DIRECTORY and the current date.

    Returns:
        bool: True if voiceover was generated and saved successfully, False otherwise.
        str: The actual path where the file was saved, or None if failed.
    """
    if not clientE:
        print("Error: ElevenLabs client is not initialized. Cannot generate voiceover.")
        return False, None

    if not script:
        print("Error: No script provided for voiceover generation.")
        return False, None

    if not original_save_path_from_app:
        print("Error: No original_save_path_from_app provided for voiceover generation.")
        return False, None

    try:
        # --- Determine the final save path ---
        # 1. Get the current date string (YYYY-MM-DD)
        current_date_str = datetime.now().strftime("%Y-%m-%d") # This will be "2025-05-13"

        # 2. Create the date-specific directory path
        date_specific_dir = os.path.join(BASE_SAVE_DIRECTORY, current_date_str)

        # 3. Extract the desired filename from the path provided by app.py
        target_filename = os.path.basename(original_save_path_from_app)
        if not target_filename: # Handle cases like "some/dir/"
            print("Error: Could not extract a valid filename from original_save_path_from_app.")
            return False, None
        if not target_filename.lower().endswith(".mp3"): # Ensure it's an mp3
             target_filename += ".mp3"


        # 4. Construct the final full path for saving the audio
        final_save_path = os.path.join(date_specific_dir, target_filename)

        print(f"🎤 Generating voiceover for script. Target save path: {final_save_path}")

        # --- Ensure the target directory exists ---
        os.makedirs(date_specific_dir, exist_ok=True)
        print(f"Ensured save directory exists: {date_specific_dir}")

        # Generate audio using Adam's voice
        audio = clientE.text_to_speech.convert(
            text=script,
            voice_id="pNInz6obpgDQGcFmaJgB",  # Adam voice ID
            model_id="eleven_multilingual_v2", # Or your preferred model
            output_format="mp3_44100_128" # Recommended format
        )

        # Save the MP3 using the constructed final_save_path
        save(audio, final_save_path)
        print(f"✅ MP3 successfully saved to: {final_save_path}")

        return True, final_save_path

    except Exception as e:
        print(f"❌ An error occurred during ElevenLabs voiceover generation: {e}")
        # import traceback
        # traceback.print_exc() # Uncomment for detailed error tracing
        return False, None


# Example usage (if you were to run this script directly for testing):
if __name__ == "__main__":
    print(f"Current Date for folder structure: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Base save directory: {BASE_SAVE_DIRECTORY}")

    # Ensure client is initialized for standalone test
    if clientE:
        test_script = "Hello, this is a test voiceover generated on May 13th, 2025."
        # app.py might provide a path like this, or just "test_audio.mp3"
        test_original_path = "project_x/temp_files/test_audio.mp3"

        success, saved_file_path = fetch_voiceover(test_script, test_original_path)

        if success:
            print(f"Test voiceover generated and saved to: {saved_file_path}")
            # You could add playback here if desired for testing
            # if os.path.exists(saved_file_path):
            #     try:
            #         print(f"Attempting to play: {saved_file_path}")
            #         play(open(saved_file_path, 'rb').read()) # elevenlabs.play takes audio bytes
            #     except Exception as e:
            #         print(f"Error playing audio: {e}")
        else:
            print("Test voiceover generation failed.")

        # Test with just a filename
        success_fn, saved_file_path_fn = fetch_voiceover("Another test.", "simple_test.mp3")
        if success_fn:
            print(f"Test voiceover (filename only) generated and saved to: {saved_file_path_fn}")
        else:
            print("Test voiceover (filename only) generation failed.")

    else:
        print("Cannot run test: ElevenLabs client not initialized (check API key and path).")