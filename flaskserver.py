import os
import json
import re
import shutil
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
# Assuming voiceoverai.py is in the same directory and has a fetch_voiceover function
from voiceoverai import fetch_voiceover # Ensure this module exists and works
from openai import OpenAI
from datetime import date # Import date to get the current date

# --- Import the video processing functions from video_assembly.py ---
# Make sure video_assembly.py is in the same directory as app.py
try:
    from video_assembler import create_video_from_ordered_images, remove_silence, speed_up_audio, get_duration
    print("Successfully imported video processing functions from video_assembly.py")
    VIDEO_PROCESSING_AVAILABLE = True
except ImportError as e:
    print(f"Error: Could not import video_assembly.py: {e}")
    print("Video creation functionality will not be available.")
    # Define dummy functions if import fails to prevent errors later
    def create_video_from_ordered_images(*args, **kwargs):
        print("Dummy create_video_from_ordered_images called (video_assembly.py not found)")
        return False
    def remove_silence(*args, **kwargs):
         print("Dummy remove_silence called")
         return False
    def speed_up_audio(*args, **kwargs):
         print("Dummy speed_up_audio called")
         return False
    def get_duration(*args, **kwargs):
         print("Dummy get_duration called")
         return 0
    VIDEO_PROCESSING_AVAILABLE = False # Flag to indicate if import failed


# Set the output directories
# Make these directories relative to the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Frontend expects images from /shorts/output/YYYY-MM-DD/
# Assuming app.py is in the 'shorts' directory and 'output' is directly inside 'shorts'
# The base directory for images should be <SCRIPT_DIR>/output
IMAGE_BASE_DIR = os.path.join(SCRIPT_DIR, "output") # Corrected path construction

VOICEOVER_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "voiceovers") # Directory for voiceover files
VIDEO_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "videos") # Directory for final video files
TEMP_AUDIO_DIR = os.path.join(SCRIPT_DIR, "temp_audio") # Directory for temporary audio files (silence removed, speed up)


# Ensure output directories exist
os.makedirs(IMAGE_BASE_DIR, exist_ok=True)
os.makedirs(VOICEOVER_OUTPUT_DIR, exist_ok=True)
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)


app = Flask(__name__)
CORS(app)

# Set demo mode (1 for test data, 0 for real API)
DEMO_MODE = 0 # Keep DEMO_MODE = 0 for real API calls in this section

# Initialize OpenAI client
client = None # Initialize client to None
try:
    # Read API key securely
    # Use os.path.join for cross-platform compatibility
    api_key_path = os.path.join('E:', 'mydeepseek.txt')
    with open(api_key_path, 'r') as file:
        api_key = file.read().strip()
    if not api_key:
         raise ValueError("DeepSeek API key not found in file")
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    print("OpenAI client (for DeepSeek) initialized successfully.")
except FileNotFoundError:
    print(f"Error: '{api_key_path}' not found. DeepSeek API will not be available.")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    print("Warning: DeepSeek API will not be available.")


# --- System messages (Keep as is) ---
PROMPT_GENERATION_SYSTEM = """
You are a YouTube Shorts video creator assistant. Your task is to generate high-quality image generation prompts based on a given topic.

Rules for prompts:
1. Each prompt must describe a vivid, cinematic scene that is ideal for AI image generation.
2. Use rich, descriptive language that captures specific visual elements.
3. Each prompt should be self-contained and between 10 words long.
4. Prompts must be diverse, representing different scenes or key moments.
5. Begin each prompt with a visually striking hook.

Return ONLY a JSON array with prompt strings.
"""

SCRIPT_GENERATION_SYSTEM = """
You are a YouTube Shorts script writer. high-retention scripts that instantly hook viewers, maintain suspense, and end with a compelling call-to-action, deliver value quickly, and boost engagement.

Script Guidelines:
1. Duration: Keep each script under 60 seconds (100–150 words).
2. Hook: Begin with a bold, attention-grabbing statement in the first 3 seconds.
3. Language: Use simple, clear, and conversational language—avoid complex or formal wording.
4. Structure: Hook → 3 engaging key points → Conclusion with a strong call-to-action (CTA).
5. Flow: Ensure smooth, natural transitions between lines. Every sentence should keep the viewer interested.
6. Tone: Fast-paced, energetic, and compelling—no fluff or filler.
7. Style Rules:
    - Do not use emojis.
    - Do not include section labels like [Hook] or [CTA].
    - Write in plain, voiceover-ready text.

Output Format:
Return the complete script as plain text only—no labels, no formatting instructions, just the final script.
"""

# --- Helper functions (Keep ai_generate and extract_json_array) ---
def ai_generate(prompt, system_message):
    if not client:
        raise RuntimeError("AI client not initialized. Cannot generate content.")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        stream=False
    )
    return response.choices[0].message.content

def extract_json_array(text):
    """Extract JSON array from potentially malformed text response"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    # Fallback: try splitting by lines if JSON fails
    if isinstance(text, str):
         lines = [line.strip() for line in text.split('\n') if line.strip()]
         if lines:
              # Attempt to clean up common list prefixes like numbers or bullet points
              cleaned_lines = [re.sub(r'^\d+\.\s*', '', line) for line in lines] # Remove numbered list prefix
              cleaned_lines = [re.sub(r'^[\-\*\+]\s*', '', line) for line in cleaned_lines] # Remove bullet points
              return [line.strip() for line in cleaned_lines if line.strip()] # Return cleaned non-empty lines

    return None # Return None if extraction fails


# --- Flask Routes ---

@app.route('/generate-prompts', methods=['POST'])
def generate_prompts():
    data = request.get_json()
    topic = data.get('video_idea', '')
    num_prompts = data.get('num_prompts', '5') # Default to 5 prompts

    if not topic:
        return jsonify({'error': 'Missing video_idea'}), 400

    try:
        num_prompts_int = int(num_prompts)
        if num_prompts_int <= 0:
             return jsonify({'error': 'num_prompts must be a positive integer'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid num_prompts value'}), 400


    if DEMO_MODE == 1:
         print(f"Demo Mode: Generating {num_prompts_int} image prompts about: {topic}")
         prompts = [
             "A breathtaking view of Niagara Falls from the Canadian side with rainbow in the mist",
             "Angel Falls in Venezuela cascading down the tabletop mountain",
             "Iguazu Falls with its hundreds of cascades surrounded by lush rainforest",
             "Victoria Falls with its massive curtain of water creating a permanent rainbow",
             "Plitvice Lakes waterfalls in Croatia with their turquoise waters and lush surroundings"
         ][:num_prompts_int] # Slice demo data to match requested quantity
    else:
        if not client:
             return jsonify({'error': 'AI client not available for real generation'}), 500
        try:
            print(f"Generating {num_prompts_int} image prompts about: {topic}")
            # Instruct AI to generate the exact number of prompts
            # Requesting JSON array format explicitly
            prompt = f"Generate exactly {num_prompts_int} distinct, vivid image generation prompts about: {topic}. Return the output as a JSON array of strings, like [\"Prompt 1\", \"Prompt 2\", ...]. Do not include any other text."
            response = ai_generate(prompt, PROMPT_GENERATION_SYSTEM)
            prompts = extract_json_array(response)

            print(f"Generated (raw): {response}")
            print(f"Extracted prompts: {prompts}")

            # Robust check: Ensure prompts is a list and has the expected number of items
            if not isinstance(prompts, list) or len(prompts) != num_prompts_int:
                 print(f"Warning: Generated prompts format incorrect or count mismatch. Expected {num_prompts_int}, got {len(prompts) if isinstance(prompts, list) else 'non-list'}.")
                 # Attempt fallback extraction if initial JSON parsing failed but response is string
                 if isinstance(response, str):
                      fallback_prompts = extract_json_array(response) # extract_json_array has fallback logic
                      if isinstance(fallback_prompts, list) and len(fallback_prompts) >= num_prompts_int:
                           prompts = fallback_prompts[:num_prompts_int]
                           print(f"Using fallback extraction, successfully got {len(prompts)} prompts.")
                      elif isinstance(fallback_prompts, list) and len(fallback_prompts) > 0:
                           prompts = fallback_prompts
                           print(f"Using fallback extraction, got {len(prompts)} prompts (less than requested).")
                      else:
                           prompts = [] # Fallback failed too


            if not prompts or len(prompts) == 0:
                 # If after all attempts, we have no prompts, raise error
                 raise ValueError("Failed to generate valid prompts.")

            # Ensure the returned list has the exact requested number, even if fallback got more
            # If fallback got less, we return what we got, but log a warning.
            if len(prompts) != num_prompts_int:
                 print(f"Warning: Final prompt count ({len(prompts)}) does not match requested count ({num_prompts_int}).")
                 # Decide if this should be an error or just a warning. Let's allow partial results for now.


        except Exception as e:
            print(f"Error generating prompts: {str(e)}")
            return jsonify({
                'error': 'Failed to generate prompts',
                'details': str(e)
            }), 500

    # Return the generated prompts (may be less than requested if AI/fallback failed)
    return jsonify({'prompts': prompts})


@app.route('/generate-voiceover', methods=['POST'])
def generate_voiceover():
    data = request.get_json()
    script = data.get('script', '')
    # voice_type = data.get('voice_type', '1') # Assuming this is not used in fetch_voiceover yet
    save_name_base = data.get('save_name', 'voiceover_temp') # Default save name without extension

    if not script:
        return jsonify({'error': 'Missing script'}), 400

    # --- Always add .mp3 extension in backend ---
    save_filename = f"{save_name_base}.mp3"
    save_path = os.path.join(VOICEOVER_OUTPUT_DIR, save_filename)
    print(f"Attempting to save voiceover to: {save_path}")

    if DEMO_MODE == 1:
        print(f"Demo Mode: Generating voiceover for script (saving as {save_filename})")
        # Simulate saving a dummy file in demo mode
        try:
            # Create parent directory if it doesn't exist (already done on startup, but safe)
            os.makedirs(VOICEOVER_OUTPUT_DIR, exist_ok=True)
            with open(save_path, 'w') as f:
                f.write("This is a dummy voiceover file.")
            message = "Demo voiceover generated successfully"
            success = True
        except Exception as e:
            print(f"Demo Mode: Failed to simulate saving voiceover: {e}")
            message = "Demo voiceover simulation failed"
            success = False
            # Return an error status for demo failure
            return jsonify({
                'error': 'Failed to save demo voiceover file',
                'details': str(e)
            }), 500

    else:
        try:
            print(f"Real Mode: Generating voiceover for script (saving as {save_filename})")
            # Call your actual voice generation function from voiceoverai
            # ASSUMPTION: fetch_voiceover(script, output_filepath) saves the file and returns True on success
            # You MUST modify voiceoverai.py's fetch_voiceover to accept the full path
            success = fetch_voiceover(script, save_path)

            if not success:
                # Assuming fetch_voiceover returns False or None on failure
                 raise RuntimeError("fetch_voiceover function reported failure")

            message = "Voiceover generated successfully"
            success = True

        except ImportError:
             print("voiceoverai module not found. Cannot generate real voiceover.")
             return jsonify({
                 'error': 'Voiceover module not available',
                 'details': 'The voiceoverai.py module could not be imported.'
             }), 500
        except Exception as e:
            print(f"Error generating voiceover: {str(e)}")
            return jsonify({
                'error': 'Failed to generate voiceover',
                'details': str(e)
            }), 500

    # Return success response with the generated filename
    # The frontend expects just the filename, not the full server path
    return jsonify({
        'message': message,
        'filename': save_filename, # Return the filename with .mp3 added by backend
        'success': success
    })


@app.route('/generate-script', methods=['POST'])
def generate_script():
    data = request.get_json()
    topic = data.get('video_idea', '')

    if not topic:
        return jsonify({'error': 'Missing video_idea'}), 400


    if DEMO_MODE == 1:
        print(f"Demo Mode: Generating script about: {topic}")
        script = f"""DEMO SCRIPT: {topic}

Did you know these amazing facts about {topic}? Get ready to be surprised!

First fact: Elaborate on the first amazing detail. Make it sound exciting!

Second fact: Reveal the second incredible piece of information. Keep the energy high!

Third fact: Share the most surprising aspect that changes everything you thought you knew!

Liked these facts? Hit that like button and follow for more mind-blowing content!""" # More realistic demo script
        # Simulate delay
        # import time
        # time.sleep(1)

    else:
        if not client:
             return jsonify({'error': 'AI client not available for real generation'}), 500
        try:
            print(f"Real Mode: Generating script about: {topic}")
            prompt = f"Create a script about: {topic}"
            script = ai_generate(prompt, SCRIPT_GENERATION_SYSTEM)

            if not script or len(script.strip()) < 50: # Increased minimum length for a useful script
                 raise ValueError("Script generation failed or resulted in a very short script")

            # Optional: Basic cleanup of potential unwanted characters or markdown
            script = script.strip()
            # Remove potential leading/trailing quotes if the AI sometimes wraps the output
            if script.startswith('"') and script.endswith('"'):
                 script = script[1:-1]


        except Exception as e:
            print(f"Error generating script: {str(e)}")
            return jsonify({
                'error': 'Failed to generate script',
                'details': str(e)
            }), 500

    return jsonify({'script': script})


# --- Route to serve images from the dated output folder ---
# The JS expects http://localhost//shorts//output//${dateString}//${filename}-0.png
# This route maps /shorts/output/YYYY-MM-DD/filename.png to the actual file path
@app.route('/shorts/output/<year>/<month>/<day>/<filename>')
def serve_dated_image(year, month, day, filename):
    # Construct the full directory path for the specific date
    # Use os.path.join with IMAGE_BASE_DIR which is now relative to script location
    dated_image_dir = os.path.join(IMAGE_BASE_DIR, f"{year}-{month}-{day}")
    # Ensure the directory exists and the filename is safe
    # Add check for the specific file path as well
    file_path = os.path.join(dated_image_dir, filename)
    if not os.path.isdir(dated_image_dir) or not os.path.exists(file_path) or '..' in filename or filename.startswith('/'):
        print(f"Image file not found or path unsafe: {file_path}")
        return "File not found", 404
    print(f"Serving image from: {dated_image_dir} filename: {filename}")
    try:
        # Use safe send_from_directory
        return send_from_directory(dated_image_dir, filename)
    except FileNotFoundError:
        # This should ideally be caught by os.path.exists, but as a fallback
        print(f"send_from_directory could not find file: {file_path}")
        return "File not found", 404
    except Exception as e:
         print(f"Error serving image: {e}")
         return "Internal Server Error", 500


# --- NEW: Route to create the video ---
@app.route('/create-video', methods=['POST'])
def create_video_route(): # Renamed function to avoid conflict with imported function
    # Check if video processing functions were imported successfully
    if not VIDEO_PROCESSING_AVAILABLE:
         print("Video processing functions not available due to import error.")
         return jsonify({'success': False, 'message': 'Video processing functions are not available on the server. Check server logs for video_assembly.py import errors.'}), 500


    data = request.get_json()
    unique_id = data.get('unique_id')
    # script = data.get('script') # Script might not be needed for video creation itself, but useful for logging/debugging
    image_filenames = data.get('image_filenames', []) # Ordered list of filenames (e.g., ['Gen12345_abcde_1', 'Gen12345_fghij_2'])
    voiceover_filename = data.get('voiceover_filename') # e.g., 'Gen12345_klmno.mp3'

    if not all([unique_id, image_filenames, voiceover_filename]):
        return jsonify({'success': False, 'message': 'Missing required parameters (unique_id, image_filenames, voiceover_filename)'}), 400

    if not isinstance(image_filenames, list) or not image_filenames:
         return jsonify({'success': False, 'message': 'image_filenames must be a non-empty list'}), 400

    # Get the current date to construct the image paths
    today_str = date.today().strftime("%Y-%m-%d")
    # Use os.path.join with IMAGE_BASE_DIR which is now relative to script location
    dated_image_dir = os.path.join(IMAGE_BASE_DIR, today_str) # Base directory for today's images

    # --- Use voiceover_filename directly as provided by frontend ---
    voiceover_path = os.path.join(VOICEOVER_OUTPUT_DIR, voiceover_filename) # Full path to voiceover file

    # Define paths for temporary processed audio files
    # Use os.path.splitext to reliably get the base name without extension
    voiceover_base_name, _ = os.path.splitext(voiceover_filename)

    audio_no_silence_filename = f"{voiceover_base_name}_no_silence.mp3"
    audio_speed_up_filename = f"{voiceover_base_name}_speedup.mp3"
    audio_no_silence_path = os.path.join(TEMP_AUDIO_DIR, audio_no_silence_filename)
    audio_speed_up_path = os.path.join(TEMP_AUDIO_DIR, audio_speed_up_filename)


    # Define the output video path
    output_video_filename = f"shorts_video_{unique_id}.mp4" # Unique output filename
    output_video_path = os.path.join(VIDEO_OUTPUT_DIR, output_video_filename)

    print(f"Received request to create video: {unique_id}")
    print(f"Image filenames: {image_filenames}")
    print(f"Voiceover filename: {voiceover_filename}")
    print(f"Output video path: {output_video_path}")


    # Use a try...finally block to ensure temporary audio files are cleaned up
    try:
        # 1. Construct full image paths from filenames and verify existence
        image_paths = []
        for filename in image_filenames:
            # Assuming image files are saved with the -0.png suffix by the image API
            # The filename from frontend is 'UniqueID_randomstring_X'
            full_image_filename = f"{filename}-0.png" # Append the expected suffix
            image_path = os.path.join(dated_image_dir, full_image_filename)
            print(f"Checking for image file: {image_path}") # Added print for debugging
            if not os.path.exists(image_path):
                print(f"Image file NOT found at: {image_path}") # Added print for debugging
                # Decide how to handle: skip the image or fail the video creation?
                # Failing video creation is safer if frontend expected all images.
                return jsonify({'success': False, 'message': f'Image file not found: {full_image_filename}'}), 404
            image_paths.append(image_path)

        if not image_paths:
             return jsonify({'success': False, 'message': 'No valid image files found based on provided filenames'}), 400

        # 2. Verify voiceover file exists
        print(f"Checking for voiceover file: {voiceover_path}") # Added print for debugging
        if not os.path.exists(voiceover_path):
            print(f"Voiceover file not found: {voiceover_path}") # Added print for debugging
            return jsonify({'success': False, 'message': f'Voiceover file not found: {voiceover_filename}'}), 404

        # 3. Process audio (remove silence, speed up) using imported functions
        # Pass the original voiceover path and the temporary paths
        print("Starting audio processing...")
        # Ensure TEMP_AUDIO_DIR exists before saving temp files
        os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

        # Call the imported remove_silence function
        audio_processing_success = remove_silence(voiceover_path, audio_no_silence_path)

        if audio_processing_success:
             # Call the imported speed_up_audio function if silence removal was successful
             audio_processing_success = speed_up_audio(audio_no_silence_path, audio_speed_up_path, speed_factor=1.20)


        if not audio_processing_success:
             # If audio processing failed, return error
             return jsonify({'success': False, 'message': 'Failed to process audio (silence removal or speed up). Check server logs for video_assembly.py errors.'}), 500 # Added details


        print("Audio processing complete.")


        # 4. Create video from the ORDERED image paths and the PROCESSED audio
        print("Starting video creation from processed audio and ordered images...")
        # Call the imported create_video_from_ordered_images function
        video_creation_success = create_video_from_ordered_images(image_paths, audio_speed_up_path, output_video_path)


        if not video_creation_success:
             # If video creation failed, return error
             # The create_video_from_ordered_images function should print details
             return jsonify({'success': False, 'message': 'Failed to combine images and audio into video. Check server logs for video_assembly.py errors or FFmpeg issues.'}), 500 # Added details


        print("Video creation complete.")

        # 5. Return success response
        # Return a URL where the video can be accessed via the /videos route
        return jsonify({
            'success': True,
            'message': 'Video created successfully!',
            'video_path': output_video_path, # Optional: return server path
            'video_url': f'/videos/{os.path.basename(output_video_path)}' # URL for frontend to access (use basename)
        })

    except Exception as e:
        # Catch any unexpected errors during the Flask route execution
        print(f"An unexpected error occurred during video creation process: {str(e)}")
        # import traceback # Uncomment for detailed error tracing
        # traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred during video creation',
            'details': str(e)
        }), 500

    finally:
        # 6. Clean up temporary audio files in a finally block
        print("Cleaning up temporary audio files...")
        if os.path.exists(audio_no_silence_path):
            try:
                os.remove(audio_no_silence_path)
                print(f"Deleted temporary file: {audio_no_silence_path}")
            except Exception as e:
                print(f"Error cleaning up temp file {audio_no_silence_path}: {e}")
        if os.path.exists(audio_speed_up_path):
            try:
                os.remove(audio_speed_up_path)
                print(f"Deleted temporary file: {audio_speed_up_path}")
            except Exception as e:
                 print(f"Error cleaning up temp file {audio_speed_up_path}: {e}")
        # Clean up partial video file if creation failed and it exists/is empty
        if os.path.exists(output_video_path) and (os.path.getsize(output_video_path) == 0 or not video_creation_success):
             try:
                 os.remove(output_video_path)
                 print(f"Cleaned up empty or failed video file: {output_video_path}")
             except Exception as e:
                 print(f"Error cleaning up failed video file {output_video_path}: {e}")


# --- Route to serve the final video file ---
# The JS expects http://localhost/videos/filename.mp4 (example URL)
@app.route('/videos/<filename>')
def serve_video(filename):
    # Ensure the directory exists and the filename is safe
    file_path = os.path.join(VIDEO_OUTPUT_DIR, filename)
    if not os.path.exists(file_path) or '..' in filename or filename.startswith('/'):
        print(f"Video file not found or path unsafe: {file_path}")
        return "File not found", 404
    print(f"Serving video file: {filename} from {VIDEO_OUTPUT_DIR}")
    try:
        # Use safe send_from_directory
        return send_from_directory(VIDEO_OUTPUT_DIR, filename)
    except FileNotFoundError:
        # This should ideally be caught by os.path.exists, but as a fallback
        print(f"send_from_directory could not find file: {file_path}")
        return "File not found", 404
    except Exception as e:
         print(f"Error serving video: {e}")
         return "Internal Server Error", 500


if __name__ == '__main__':
    # Ensure image output directory has the date subfolder for today
    today_str = date.today().strftime("%Y-%m-%d")
    # Use os.path.join with IMAGE_BASE_DIR which is now relative to script location
    os.makedirs(os.path.join(IMAGE_BASE_DIR, today_str), exist_ok=True)
    print(f"Serving images from {os.path.abspath(IMAGE_BASE_DIR)}")
    print(f"Serving voiceovers from {os.path.abspath(VOICEOVER_OUTPUT_DIR)}")
    print(f"Serving videos from {os.path.abspath(VIDEO_OUTPUT_DIR)}")
    print(f"Using temporary audio directory: {os.path.abspath(TEMP_AUDIO_DIR)}")


    # Run the Flask app
    # Make sure your image generation service is running on 127.0.0.1:8888
    # Make sure FFmpeg is installed and in your system's PATH for video_assembly.py
    app.run(host='0.0.0.0', port=5000, debug=True)
