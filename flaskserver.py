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

# System messages
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
You are a YouTube Shorts script writer. Create engaging, concise scripts for short videos.

Rules:
1. Keep it under 60 seconds (100-150 words max)
2. Start with a strong hook (first 3 seconds)
3. Use simple, conversational language
4. Include clear section transitions
5. End with a call-to-action (like, follow, etc.)
6. Structure: Hook -> 3 main points -> Conclusion

Format:
[Opening Hook]
[Main Content - 3 key points]
[Closing & CTA]
"""

def ai_generate(prompt, system_message):
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
    return None

@app.route('/generate-prompts', methods=['POST'])
def generate_prompts():
    data = request.get_json()
    topic = data.get('video_idea', '')
    num_prompts = data.get('num_prompts','')

    if DEMO_MODE == 1:
        prompts = [
            "A breathtaking view of Niagara Falls from the Canadian side with rainbow in the mist",
            "Angel Falls in Venezuela cascading down the tabletop mountain",
            "Iguazu Falls with its hundreds of cascades surrounded by lush rainforest",
            "Victoria Falls with its massive curtain of water creating a permanent rainbow",
            "Plitvice Lakes waterfalls in Croatia with their turquoise waters and lush surroundings"
        ]
    else:
        try:
            print(f"Generating {num_prompts} image prompts about: {topic}")
            prompt = f"Generate exactly {num_prompts} image prompts about: {topic}"
            response = ai_generate(prompt, PROMPT_GENERATION_SYSTEM)
            prompts = extract_json_array(response)
            
            print(f"Generated{prompts}")
            print(f"debug{len(prompts)} and {num_prompts}")

            numpromptint = int(num_prompts)
            if not prompts or len(prompts) != numpromptint:
                raise ValueError("Invalid prompt format received")
                
        except Exception as e:
            print(f"Error generating prompts: {str(e)}")
            return jsonify({
                'error': 'Failed to generate prompts',
                'details': str(e)
            }), 500

    return jsonify({'prompts': prompts})

@app.route('/generate-script', methods=['POST'])
def generate_script():
    data = request.get_json()
    topic = data.get('video_idea', '')

    if DEMO_MODE == 1:
        script = f"""DEMO SCRIPT: {topic}

[Opening Hook]
Did you know these amazing facts about {topic}? Stick around to see them all!

[Main Content]
1. First amazing fact with visual demonstration
2. Second incredible detail you won't believe
3. The most surprising aspect that changes everything

[Closing & CTA]
Which fact surprised you most? Like and follow for more amazing content!"""
    else:
        try:
            prompt = f"Create a YouTube Shorts script about: {topic}"
            script = ai_generate(prompt, SCRIPT_GENERATION_SYSTEM)
            
            if not script or len(script) < 20:
                raise ValueError("Script generation failed")
                
        except Exception as e:
            print(f"Error generating script: {str(e)}")
            return jsonify({
                'error': 'Failed to generate script',
                'details': str(e)
            }), 500

    return jsonify({'script': script})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)