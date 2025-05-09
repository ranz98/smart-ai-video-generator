import os
from elevenlabs.client import ElevenLabs
from elevenlabs import save
import re


with open('E:\elevenlabsapi.txt', 'r') as file:
    api_key = file.read().strip()


client = ElevenLabs(api_key=api_key)

def fetch_voiceover(script,filenamex):
    # Open the input text file
   # with open(input_file, 'r') as file:
     #   content = file.read()
    print("Generating voiceover......")
    filename = re.sub(r'[^a-zA-Z0-9\s]', '', filenamex) + ".mp3"

    # Convert text to speech using the Adam voice
    audio = client.text_to_speech.convert(
        text=script,
        voice_id="pNInz6obpgDQGcFmaJgB",  # Set to the "Adam" voice ID
        model_id="eleven_multilingual_v2",  # The model ID for multilingual voices
        output_format="mp3_44100_128",  # Output format: MP3 at 44.1kHz and 128kbps
    )

    save(audio, filename)
    print(f"✅ MP3 file saved as {filename}")
