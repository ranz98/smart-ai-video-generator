from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import json
import re

app = Flask(__name__)
CORS(app)

# Set demo mode (1 for test data, 0 for real API)
DEMO_MODE = 0

# Initialize OpenAI client
with open('E:\mydeepseek.txt', 'r') as file:
    api_key = file.read().strip()

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# System message with prompt generation instructions
SYSTEM_MESSAGE = """
You are a YouTube Shorts video creator assistant. Your task is to generate exactly 5 high-quality image generation prompts based on a given topic.

Rules for prompts:
1. Each prompt must describe a vivid, cinematic scene that is ideal for AI image generation.
2. Use rich, descriptive language that captures specific visual elements—such as clothing, background setting, mood, lighting, props, and composition.
3. Each prompt should be self-contained and between 10 words long.
4. Prompts must be diverse, representing different scenes, perspectives, or key moments related to the topic.
5. Begin each prompt with a visually striking hook to immediately draw the viewer in.
6. Use a storytelling tone—each prompt should feel like a snapshot from a powerful movie or historical drama.

Output format requirements:
- Return ONLY a JSON array with exactly 5 prompt strings
- Do not include any additional text or explanations
- Do not number the prompts
"""

def ai_generate(prompt):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": prompt}
        ],
        stream=False
    )
    return response.choices[0].message.content

def extract_json_array(text):
    """Extract JSON array from potentially malformed text response"""
    try:
        # Try direct JSON parsing first
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: Extract array content between [ and ]
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    return None

@app.route('/generate-prompts', methods=['POST'])
def generate_prompts():
    data = request.get_json()
    topic = data.get('video_idea', '')
    num_prompts = data.get('num_prompts', 5)

    if DEMO_MODE == 1:
        # Demo data
        prompts = [
            "A breathtaking view of Niagara Falls from the Canadian side with rainbow in the mist",
            "Angel Falls in Venezuela cascading down the tabletop mountain",
            "Iguazu Falls with its hundreds of cascades surrounded by lush rainforest",
            "Victoria Falls with its massive curtain of water creating a permanent rainbow",
            "Plitvice Lakes waterfalls in Croatia with their turquoise waters and lush surroundings"
        ]
    else:
        try:
            prompt = f"""
            Generate exactly {num_prompts} about: {topic}

            
            Return ONLY a JSON array with the prompt strings.
            """
            
            response = ai_generate(prompt)
            prompts = extract_json_array(response)
            
            if not prompts or len(prompts) != num_prompts:
                raise ValueError("Invalid prompt format received")
                
        except Exception as e:
            print(f"Error generating prompts: {str(e)}")
            return jsonify({
                'error': 'Failed to generate prompts',
                'details': str(e)
            }), 500

    return jsonify({'prompts': prompts})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)