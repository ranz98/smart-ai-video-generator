import os
import re
from datetime import datetime
from elevenlabs.client import ElevenLabs
from elevenlabs import save, play # Keep play if you use it elsewhere, otherwise can remove

# Load API key
# Use os.path.join for cross-platform compatibility
api_key_path = r'E:\elevenlabsapi.txt'
try:
    with open(api_key_path, 'r') as file:
        api_keyE = file.read().strip()
    if not api_keyE:
        raise ValueError("ElevenLabs API key is empty.")
    print("ElevenLabs API key loaded successfully.")
except FileNotFoundError:
    print(f"Error: ElevenLabs API key file not found at {api_key_path}")
    api_keyE = None # Set to None if file not found
except Exception as e:
    print(f"Error loading ElevenLabs API key: {e}")
    api_keyE = None # Set to None on other errors


# Initialize ElevenLabs client
clientE = None # Initialize client to None
if api_keyE:
    try:
        clientE = ElevenLabs(api_key=api_keyE)
        # Optional: Test a simple call to verify the key/client
        # clientE.voices.get_all()
        print("ElevenLabs client initialized successfully.")
    except Exception as e:
        print(f"Error initializing ElevenLabs client: {e}")
        clientE = None # Set to None if initialization fails


def fetch_voiceover(script, save_path):
    """
    Generates voiceover for the given script using ElevenLabs API
    and saves the audio to the specified file path.

    Args:
        script (str): The text script to convert to speech.
        save_path (str): The full path (including filename and .mp3 extension)
                         where the generated audio should be saved. This path
                         is provided by app.py and should be used directly.

    Returns:
        bool: True if voiceover was generated and saved successfully, False otherwise.
    """
    if not clientE:
        print("Error: ElevenLabs client is not initialized. Cannot generate voiceover.")
        return False

    if not script:
        print("Error: No script provided for voiceover generation.")
        return False

    if not save_path:
         print("Error: No save_path provided for voiceover generation.")
         return False

    print(f"🎤 Generating voiceover for script and attempting to save directly to: {save_path}")

    try:
        # --- CORRECT: Ensure the target directory exists ---
        # app.py should create the base voiceovers directory, but ensure the specific
        # directory for this save_path exists just in case (e.g., if subfolders were used)
        save_dir = os.path.dirname(save_path)
        os.makedirs(save_dir, exist_ok=True)
        print(f"Ensured save directory exists: {save_dir}")


        # Generate audio using Adam's voice
        # Use the clientE object initialized globally
        audio = clientE.text_to_speech.convert(
            text=script,
            voice_id="pNInz6obpgDQGcFmaJgB",  # Adam voice ID
            model_id="eleven_multilingual_v2", # Or your preferred model
            output_format="mp3_44100_128" # Recommended format
        )

        # Save the MP3 using the provided save_path
        # The `save` function from elevenlabs handles writing the audio data
        save(audio, save_path)
        print(f"✅ MP3 successfully saved to: {save_path}")

        return True # Explicitly return True on successful generation and saving

    except Exception as e:
        print(f"❌ An error occurred during ElevenLabs voiceover generation: {e}")
        # import traceback
        # traceback.print_exc() # Uncomment for detailed error tracing
        return False # Return False to indicate failure to app.py


# You can add other helper functions or standalone script logic here if needed
# The main function from your previous script is not needed for integration with Flask
# as Flask will call fetch_voiceover directly.

# Example of how you might use play (if needed elsewhere)
# def play_voiceover(audio_path):
#     if os.path.exists(audio_path):
#         try:
#             play(audio_path)
#             print(f"Playing audio from {audio_path}")
#         except Exception as e:
#             print(f"Error playing audio: {e}")
#     else:
#         print(f"Audio file not found for playback: {audio_path}")

