import os
import json
import re
import shutil
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
# Assuming voiceoverai.py is in the same directory and has a fetch_voiceover function
from video_creator import create_videox # Should now return the file path
from voiceoverai import fetch_voiceover # Ensure this module exists and works
from capcutapii import *
from openai import OpenAI
from datetime import date # Import date to get the current date

# Set the output directories
# Make these directories relative to the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Frontend expects images from /shorts/output/YYYY-MM-DD/
# Assuming app.py is in the 'shorts' directory and 'output' is directly inside 'shorts'
# The base directory for images should be <SCRIPT_DIR>/output
# NOTE: If your BASE_OUTPUT_FOLDER in video_creator.py is different
# like D:\Program Files\xampp\htdocs\shorts\output,
# ensure this path is consistent or handle it appropriately.
# For serving purposes, Flask should serve from the directory where the files are saved.
# The serving route /shorts/output/... needs to map to that directory.
# Let's assume for serving, we map the URL structure to the actual save location.
# The BASE_OUTPUT_FOLDER in video_creator determines where files are saved.
# We need to ensure the serve_dated_image route points to the correct base.
# Let's align the serving base with the saving base for simplicity.

# Use the same base path as video_creator for image serving consistency
# This assumes your Flask app has access to this path.
IMAGE_BASE_DIR_SERVE = r"D:\Program Files\xampp\htdocs\shorts\output" # Must match BASE_OUTPUT_FOLDER in video_creator.py

# Voiceovers are saved locally relative to app.py, but not served directly by filename
VOICEOVER_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "voiceovers") # Directory for voiceover files

# Videos are saved by video_creator.py in the IMAGE_BASE_DIR_SERVE dated folder
# but the Flask app needs to know where to serve them *from*.
# Let's assume for serving videos, we will also look in the dated folders within IMAGE_BASE_DIR_SERVE.
# So the serve_video route needs adjustment to look in the dated folder.
# Or, video_creator saves videos to a dedicated VIDEO_OUTPUT_DIR relative to app.py
# Let's revisit the app.py video serving logic based on where video_creator saves.
# Based on video_creator.py, videos are saved in the dated folder inside BASE_OUTPUT_FOLDER.
# So the /videos route should look in that dated folder.

# Directory for final video files (where video_creator saves them)
# This should match where video_creator saves, which is BASE_OUTPUT_FOLDER / YYYY-MM-DD
# Let's define a base serve path for videos, pointing to the same place images are saved.
VIDEO_SERVE_BASE_DIR = r"D:\Program Files\xampp\htdocs\shorts\output" # Must match BASE_OUTPUT_FOLDER in video_creator.py


# Ensure output directories exist (relative to app.py)
# Note: Directories for images and videos saved by video_creator.py will be created by that script
os.makedirs(VOICEOVER_OUTPUT_DIR, exist_ok=True)
# We don't need to create IMAGE_BASE_DIR_SERVE or VIDEO_SERVE_BASE_DIR here
# as video_creator.py handles creating the dated subfolders.
# Also, attempting to create D:\... might require elevated permissions depending on system.


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
    """
    API endpoint to trigger CapCut Text-to-Speech automation.
    Expects JSON body with 'script' field.
    """
    data = request.get_json()
    print("dataaa",data)

    if not data or 'script' not in data:
        return jsonify({"status": "error", "message": "Missing 'script' in request body"}), 400

    script = data['script']
    savename = data['save_name']

    # You might want to pass email/password from the request body in a real API,
    # but for this example, we'll use the configured constants.
    # email = data.get('email', CAPCUT_EMAIL)
    # password = data.get('password', CAPCUT_PASSWORD)

    print(f"Received request to generate voiceover for script: '{script}'")

    try:
        # Call the Playwright automation function
        # The function returns a dictionary including status, message, and download_path
        result = run_capcut_tts_automation(script,savename)

        # Return the result from the automation function as a JSON response
        # The automation function already formats the result dictionary appropriately
        return jsonify(result), 200

    except Exception as e:
        print(f"API Error: Automation failed: {e}")
        # Return a formatted error response if the automation fails
        return jsonify({"status": "error", "message": f"Automation failed: {str(e)}"}), 500



@app.route('/generate-voiceoverold', methods=['POST'])
def generate_voiceoverold():
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
# This route maps /shorts/output/YYYY-MM-DD/filename to the actual file path
@app.route('/shorts/output/<year>/<month>/<day>/<filename>')
def serve_dated_image(year, month, day, filename):
    # Construct the full directory path for the specific date
    # Use os.path.join with IMAGE_BASE_DIR_SERVE which points to the base output folder
    dated_image_dir = os.path.join(IMAGE_BASE_DIR_SERVE, f"{year}-{month}-{day}")
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

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request: No JSON data received.'}), 400

    unique_id = data.get('unique_id')
    if not unique_id:
        return jsonify({'success': False, 'message': 'Invalid request: Missing unique_id.'}), 400

    # The speed multiplier is hardcoded to "1.0" in the create_videox call for now.
    # If you want to make it dynamic based on frontend input,
    # you would need to add a parameter to the /create-video request.
    # For now, we assume 1.0 or update create_videox default.
    # speed_multiplier = data.get('speed_multiplier', '1.0') # Example if dynamic


    try:
        print(f"Processing /create-video request for unique_id: {unique_id}")

        # Call the imported create_videox function - now it returns the path or False
        output_video_path = create_videox(unique_id, "1.0") # Hardcoded speed for now

        if output_video_path is False:
            # If video creation failed, return error
            print("video_creator.py reported failure.")
            return jsonify({'success': False, 'message': 'Failed to combine images and audio into video. Check server logs for video_assembly.py errors or FFmpeg issues.'}), 500

        print(f"Video creation complete. File path: {output_video_path}")

        # 5. Return success response with the video URL
        video_filename = os.path.basename(output_video_path)
        # Construct the URL to serve the video.
        # The /videos route needs to be updated to handle dated folders if that's where videos are saved.
        # Based on video_creator.py saving to BASE_OUTPUT_FOLDER/YYYY-MM-DD/
        # the /videos route should also look in that dated folder.
        # Let's build the URL that the frontend can use to request the file from the updated /videos route.
        # The /videos route will need to look in the dated folder.
        # So the URL should probably also include the date.
        # e.g., /videos/YYYY-MM-DD/filename.mp4
        today_str = date.today().strftime("%Y-%m-%d")
        video_url = f'/videos/{today_str}/{video_filename}' # Construct URL including date


        return jsonify({
            'success': True,
            'message': 'Video created successfully!',
            'video_filename': video_filename, # Return the filename
           # 'video_url': video_url # Return the URL for the frontend
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



if __name__ == '__main__':
    # Ensure image output directory has the date subfolder for today
    # NOTE: video_creator.py creates this when saving images/videos,
    # but creating it here on app startup ensures it exists early.
    today_str = date.today().strftime("%Y-%m-%d")
    # Use os.path.join with IMAGE_BASE_DIR_SERVE which is the base output folder
    os.makedirs(os.path.join(IMAGE_BASE_DIR_SERVE, today_str), exist_ok=True)
    # No need to create VOICEOVER_OUTPUT_DIR here, it's handled above.
    # No need to create VIDEO_SERVE_BASE_DIR directly.

    print(f"Serving images/videos from base directory: {os.path.abspath(IMAGE_BASE_DIR_SERVE)}")
    print(f"Saving voiceovers to: {os.path.abspath(VOICEOVER_OUTPUT_DIR)}")


    # Run the Flask app
    # Make sure your image generation service is running on 127.0.0.1:8888
    # Make sure FFmpeg is installed and in your system's PATH for video_creator.py
    # Check that BASE_OUTPUT_FOLDER in video_creator.py matches the serving base paths here.
    app.run(host='0.0.0.0', port=5000, debug=True)