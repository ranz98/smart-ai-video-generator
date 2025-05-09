Here's a comprehensive GitHub README.md for your YouTube Shorts Creator project:

```markdown
# YouTube Shorts Creator 🎥⚡

![image](https://github.com/user-attachments/assets/95b11417-f157-4eb5-8a28-b0bab33bbe7f)
![image](https://github.com/user-attachments/assets/a047a73e-2718-4aa1-a02e-3842e004747e)

An AI-powered tool that generates complete YouTube Shorts content including:
- Engaging video scripts 📜
- AI-generated images 🖼️
- Ready-to-use video concepts 🎬

## Features ✨

- **One-Click Content Generation** - Get scripts and images with a single click
- **AI-Powered Prompts** - High-quality image generation prompts
- **Script Generator** - Professional YouTube Shorts scripts
- **Demo Mode** - Test without API credits
- **Responsive UI** - Works on all devices
- **Dark Mode** - Eye-friendly interface

## Tech Stack 💻

**Frontend:**
- HTML5, CSS3, JavaScript
- Bootstrap 5
- Font Awesome

**Backend:**
- Python Flask
- Open API (for text generation)
- Fooocus API (local) (for image generation)
- Foocus local server

## Installation ⚙️

### Prerequisites
- Python 3.8+
- Node.js (for optional frontend builds)
- API keys for Open Ai 

### Backend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/youtube-shorts-creator.git
   cd youtube-shorts-creator
   ```

2. Set up Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install flask flask-cors openai
   ```

4. Create a `mydeepseek.txt` file with your API key

5. Run the Flask server:
   ```bash
   python app.py
   ```

### Frontend Setup
1. Open `index.html` in your browser
2. Or serve it using a local server:
   ```bash
   python -m http.server 8000
   ```

## Configuration ⚙️

Set these environment variables or modify `app.py`:

```python
# API Configuration
DEEPSEEK_API_KEY = "your_api_key"  # Or load from file
FOOOCUS_API_URL = "http://localhost:8888/v1/generation/text-to-image"
DEMO_MODE = False  # Set to True for testing without API calls
```

## API Endpoints 🌐

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate-prompts` | POST | Generate image prompts |
| `/generate-script` | POST | Generate video script |
| `/` | GET | Frontend interface |

## Usage 🚀

1. Enter your video idea (e.g., "5 amazing facts about space")
2. Click "Generate Prompts & Script"
3. Review the generated script
4. Generate images from the prompts
5. Arrange images and create your Short

![image](https://github.com/user-attachments/assets/228bb8b6-241b-45b3-be1b-e53e95e340a3)

## Project Structure 📂

```
youtube-shorts-creator/
├── app.py                # Flask backend
├── index.html            # Main interface
├── styles.css            # Custom styles
├── mydeepseek.txt        # API key storage
├── README.md             # This file
└── assets/               # Static assets
    ├── images/           # Sample images
    └── js/               # JavaScript files
```

## Contributing 🤝

Contributions are welcome! Please follow these steps:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📜

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- DeepSeek for the AI text generation
- Fooocus for the image generation
- Bootstrap for the responsive design

---

Made with ❤️ by [Ranz98] 
```

This README includes:

1. **Project Overview** - Clear description of what the project does
2. **Key Features** - Highlighted with emojis
3. **Tech Stack** - Frontend and backend technologies
4. **Installation Guide** - Step-by-step setup instructions
5. **Configuration** - Environment variables and settings
6. **API Documentation** - Available endpoints
7. **Usage Instructions** - How to use the application
8. **Project Structure** - Directory layout
9. **Contribution Guidelines** - How others can contribute
10. **License Info** - MIT License default
11. **Acknowledgments** - Credit to dependencies
