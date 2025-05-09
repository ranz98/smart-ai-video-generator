import os
import re
from datetime import datetime
from elevenlabs.client import ElevenLabs
from elevenlabs import save

# Load API key
with open(r'E:\elevenlabsapi.txt', 'r') as file:
    api_keyE = file.read().strip()

# Initialize ElevenLabs client
clientE = ElevenLabs(api_key=api_keyE)

def fetch_voiceover(script, filenamex):
    print("🎤 Generating voiceover...")

    # Get today's date for folder name
    today = datetime.today().strftime('%Y-%m-%d')

    # Build full output path
    base_dir = r"D:\Program Files\xampp\htdocs\shorts\output"
    output_dir = os.path.join(base_dir, today)
    os.makedirs(output_dir, exist_ok=True)

    # Clean filename
    filenamez = re.sub(r'[^a-zA-Z0-9\s]', '', filenamex).strip() + ".mp3"
    output_path = os.path.join(output_dir, filenamez)

    # Generate audio using Adam's voice
    audio = clientE.text_to_speech.convert(
        text=script,
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam voice ID
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )

    # Save the MP3
    save(audio, output_path)
    print(f"✅ MP3 saved at: {output_path}")

fetch_voiceover("test", "testfilezzz")
