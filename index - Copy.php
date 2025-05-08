<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Image Generator</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-dark: #121212;
            --bg-darker: #0a0a0a;
            --card-dark: #1e1e1e;
            --accent-color: #6e48aa;
            --accent-hover: #7d5bbe;
            --text-primary: #f5f5f5;
            --text-secondary: #b3b3b3;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-primary);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }

        .navbar-brand {
            font-weight: 700;
            color: var(--accent-color);
        }

        .main-container {
            background-color: var(--bg-darker);
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            padding: 2rem;
            margin-top: 2rem;
        }

        .prompt-card {
            background-color: var(--card-dark);
            border-radius: 8px;
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .prompt-textarea {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
            resize: none;
            min-height: 150px;
        }

        .prompt-textarea:focus {
            background-color: rgba(255, 255, 255, 0.08);
            border-color: var(--accent-color);
            color: var(--text-primary);
            box-shadow: 0 0 0 0.25rem rgba(110, 72, 170, 0.25);
        }

        .btn-generate {
            background-color: var(--accent-color);
            border: none;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .btn-generate:hover {
            background-color: var(--accent-hover);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(110, 72, 170, 0.4);
        }

        .btn-generate:active {
            transform: translateY(0);
        }

        .image-placeholder {
            background-color: rgba(255, 255, 255, 0.03);
            border: 2px dashed rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            color: var(--text-secondary);
            transition: all 0.3s ease;
            position: relative;
        }

        .image-placeholder:hover {
            border-color: var(--accent-color);
            color: var(--text-primary);
        }

        .settings-card {
            background-color: var(--card-dark);
            border-radius: 8px;
        }

        .form-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .form-control, .form-select {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
        }

        .form-control:focus, .form-select:focus {
            background-color: rgba(255, 255, 255, 0.08);
            border-color: var(--accent-color);
            color: var(--text-primary);
            box-shadow: 0 0 0 0.25rem rgba(110, 72, 170, 0.25);
        }

        .footer {
            color: var(--text-secondary);
            font-size: 0.8rem;
        }

        .loader {
            display: none;
            width: 48px;
            height: 48px;
            border: 5px solid rgba(255, 255, 255, 0.1);
            border-bottom-color: var(--accent-color);
            border-radius: 50%;
            animation: rotation 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes rotation {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .generated-image {
            max-width: 100%;
            border-radius: 8px;
            display: none;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }

        .error-message {
            color: #ff6b6b;
            display: none;
            margin-top: 10px;
        }

        .filename-display {
            position: absolute;
            bottom: 10px;
            left: 10px;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.8rem;
            max-width: calc(100% - 20px);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .status-message {
            margin-top: 10px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-robot me-2"></i>AI Image Generator
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#"><i class="fas fa-history me-1"></i> History</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#"><i class="fas fa-cog me-1"></i> Settings</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-4">
        <div class="main-container">
            <div class="row">
                <div class="col-lg-8">
                    <div class="prompt-card p-4 mb-4">
                        <h5 class="mb-3"><i class="fas fa-keyboard me-2"></i>Describe your image</h5>
                        <textarea class="form-control prompt-textarea mb-3" id="promptInput" placeholder="Enter a detailed description of the image you want to generate..."></textarea>
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <button class="btn btn-sm btn-outline-secondary me-2" id="enhanceBtn">
                                    <i class="fas fa-magic me-1"></i> Enhance
                                </button>
                                <button class="btn btn-sm btn-outline-secondary" id="randomBtn">
                                    <i class="fas fa-random me-1"></i> Random
                                </button>
                            </div>
                            <span class="text-muted small" id="charCount">0/500</span>
                        </div>
                    </div>

                    <div class="image-placeholder mb-4" id="imagePlaceholder">
                        <i class="fas fa-image fa-3x mb-3" id="placeholderIcon"></i>
                        <p id="placeholderText">Your generated image will appear here</p>
                        <div class="loader" id="loader"></div>
                        <img src="" alt="Generated Image" class="generated-image" id="generatedImage">
                        <div class="filename-display" id="filenameDisplay"></div>
                        <div class="error-message" id="errorMessage"></div>
                        <div class="status-message" id="statusMessage"></div>
                    </div>
                </div>

                <div class="col-lg-4">
                    <div class="settings-card p-4 mb-4">
                        <h5 class="mb-3"><i class="fas fa-sliders-h me-2"></i>Generation Settings</h5>
                        
                        <div class="mb-3">
                            <label for="styleSelect" class="form-label">Style</label>
                            <select class="form-select" id="styleSelect">
                                <option value="Fooocus V2" selected>Fooocus V2</option>
                                <option value="Fooocus Enhance">Fooocus Enhance</option>
                                <option value="Fooocus Sharp">Fooocus Sharp</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="performanceSelect" class="form-label">Performance</label>
                            <select class="form-select" id="performanceSelect">
                                <option value="Speed" selected>Speed</option>
                                <option value="Quality">Quality</option>
                                <option value="Extreme Speed">Extreme Speed</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="aspectRatioSelect" class="form-label">Aspect Ratio</label>
                            <select class="form-select" id="aspectRatioSelect">
                                <option value="768*1344" selected>768×1344 (Portrait)</option>
                                <option value="1344*768">1344×768 (Landscape)</option>
                                <option value="1024*1024">1024×1024 (Square)</option>
                            </select>
                        </div>

                        <button class="btn btn-generate w-100 py-3" id="generateBtn">
                            <i class="fas fa-bolt me-2"></i> Generate Image
                        </button>
                    </div>

                    <div class="settings-card p-4">
                        <h5 class="mb-3"><i class="fas fa-share-alt me-2"></i>Share</h5>
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-secondary flex-grow-1">
                                <i class="fab fa-twitter me-1"></i> Twitter
                            </button>
                            <button class="btn btn-outline-secondary flex-grow-1">
                                <i class="fab fa-discord me-1"></i> Discord
                            </button>
                            <button class="btn btn-outline-secondary" id="downloadBtn" disabled>
                                <i class="fas fa-download"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="footer text-center py-3">
        <div class="container">
            <p class="mb-0">© 2023 AI Image Generator | Powered by Fooocus API</p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // DOM Elements
            const promptInput = document.getElementById('promptInput');
            const charCount = document.getElementById('charCount');
            const generateBtn = document.getElementById('generateBtn');
            const enhanceBtn = document.getElementById('enhanceBtn');
            const randomBtn = document.getElementById('randomBtn');
            const downloadBtn = document.getElementById('downloadBtn');
            const imagePlaceholder = document.getElementById('imagePlaceholder');
            const placeholderIcon = document.getElementById('placeholderIcon');
            const placeholderText = document.getElementById('placeholderText');
            const loader = document.getElementById('loader');
            const generatedImage = document.getElementById('generatedImage');
            const errorMessage = document.getElementById('errorMessage');
            const filenameDisplay = document.getElementById('filenameDisplay');
            const statusMessage = document.getElementById('statusMessage');
            const styleSelect = document.getElementById('styleSelect');
            const performanceSelect = document.getElementById('performanceSelect');
            const aspectRatioSelect = document.getElementById('aspectRatioSelect');

            // Sample prompts for random button
            const samplePrompts = [
                "A majestic lion standing on a rock at sunset, cinematic lighting",
                "Cyberpunk cityscape at night with neon lights and flying cars",
                "Portrait of an elderly wizard with a long beard and glowing eyes",
                "Futuristic spaceship landing on an alien planet with strange vegetation",
                "Cute anime-style cat wearing a samurai outfit"
            ];

            // Character counter for textarea
            promptInput.addEventListener('input', function() {
                const currentLength = this.value.length;
                charCount.textContent = `${currentLength}/500`;
                
                if (currentLength > 500) {
                    charCount.classList.add('text-danger');
                } else {
                    charCount.classList.remove('text-danger');
                }
            });

            // Enhance button - adds some common prompt enhancements
            enhanceBtn.addEventListener('click', function() {
                let prompt = promptInput.value.trim();
                if (!prompt) return;
                
                if (!prompt.toLowerCase().includes("high quality")) prompt += ", high quality";
                if (!prompt.toLowerCase().includes("4k")) prompt += ", 4k";
                if (!prompt.toLowerCase().includes("detailed")) prompt += ", detailed";
                
                promptInput.value = prompt;
                promptInput.dispatchEvent(new Event('input'));
            });

            // Random button - inserts a random sample prompt
            randomBtn.addEventListener('click', function() {
                const randomPrompt = samplePrompts[Math.floor(Math.random() * samplePrompts.length)];
                promptInput.value = randomPrompt;
                promptInput.dispatchEvent(new Event('input'));
            });

            // Download button
            downloadBtn.addEventListener('click', function() {
                if (!generatedImage.src) return;
                
                const link = document.createElement('a');
                link.href = generatedImage.src;
                link.download = generatedImage.dataset.filename || 'generated-image.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });

            // Generate button functionality
            generateBtn.addEventListener('click', async function() {
                const prompt = promptInput.value.trim();
                
                if (!prompt) {
                    showError("Please enter a description for your image");
                    return;
                }
                
                // Show loading state
                startLoading();
                updateStatus("Starting image generation...");
                
                try {
                    // Generate a random filename
                    const timestamp = new Date().getTime();
                    const randomString = Math.random().toString(10).substring(2, 8);
                    const filename = `generated-${timestamp}-${randomString}`;
                    
                    // Prepare the request data
                    const requestData = {
                        prompt: prompt,
                        style_selections: [styleSelect.value],
                        performance_selection: performanceSelect.value,
                        aspect_ratios_selection: aspectRatioSelect.value,
                        save_name: filename
                    };
                    
                    updateStatus("Sending request to API...");
                    
                    // Make the API call
                    const response = await fetch('http://127.0.0.1:8888/v1/generation/text-to-image', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(requestData)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`API request failed with status ${response.status}`);
                    }
                    
                    updateStatus("Image generation in progress...");
                    
                    // Get current date in YYYY-MM-DD format for the path
                    const today = new Date();
                    const dateString = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
                    
                    // Construct the full image path
                    const fullImagePath = `D:/PycharmProjects/fooocus/Fooocus/outputs/files/${dateString}/${filename}.jp`;
                    
                    // Display the filename immediately
                    filenameDisplay.textContent = filename;
                    filenameDisplay.style.display = 'block';
                    
                    // In a real implementation, you would need to:
                    // 1. Poll the server to check when the image is ready
                    // 2. Or have the server push a notification when done
                    
                    // For this example, we'll simulate checking for the image
                    updateStatus("Waiting for image to be generated...");
                    
                    // Simulate checking for the image (replace with actual polling in production)
                    const checkImage = async () => {
                        try {
                            // This would be an endpoint that checks if the image exists
                            // For now we'll just simulate a delay
                            await new Promise(resolve => setTimeout(resolve, 3000));
                            
                            // Once the image is ready, display it
                            // In production, you would use a server endpoint that serves the image
                            // For example: `/api/get-image?path=${encodeURIComponent(fullImagePath)}`
                            updateStatus("Image generated! Loading...");
                            
                            // For demonstration, we'll use a placeholder
                            // Replace this with actual image loading code
                            //generatedImage.src = `https://via.placeholder.com/768x1344/6e48aa/ffffff?text=${encodeURIComponent(prompt.substring(0, 30))}`;
                            generatedImage.src = `http://localhost:8009/${filename}-0.png`;

                            
                            generatedImage.alt = prompt;
                            generatedImage.dataset.filename = filename;
                            generatedImage.style.display = 'block';
                            placeholderIcon.style.display = 'none';
                            placeholderText.style.display = 'none';
                            errorMessage.style.display = 'none';
                            
                            // Enable download button
                            downloadBtn.disabled = false;
                            
                            updateStatus("Image loaded successfully!");
                            
                            // Hide status message after a delay
                            setTimeout(() => {
                                statusMessage.style.display = 'none';
                            }, 2000);
                            
                        } catch (error) {
                            console.error('Error checking for image:', error);
                            showError("Failed to load generated image");
                        }
                    };
                    
                    await checkImage();
                    
                } catch (error) {
                    console.error('Error generating image:', error);
                    showError("Failed to generate image. Please try again.");
                    updateStatus("Generation failed");
                } finally {
                    // Reset loading state
                    stopLoading();
                }
            });

            // Helper functions
            function startLoading() {
                generateBtn.disabled = true;
                generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Generating...';
                loader.style.display = 'block';
                placeholderIcon.style.display = 'none';
                placeholderText.style.display = 'none';
                generatedImage.style.display = 'none';
                errorMessage.style.display = 'none';
                filenameDisplay.style.display = 'none';
                downloadBtn.disabled = true;
                statusMessage.style.display = 'block';
            }

            function stopLoading() {
                generateBtn.disabled = false;
                generateBtn.innerHTML = '<i class="fas fa-bolt me-2"></i> Generate Image';
                loader.style.display = 'none';
            }

            function showError(message) {
                errorMessage.textContent = message;
                errorMessage.style.display = 'block';
                placeholderIcon.style.display = 'flex';
                placeholderText.style.display = 'block';
                statusMessage.style.display = 'none';
            }
            
            function updateStatus(message) {
                statusMessage.textContent = message;
                statusMessage.style.display = 'block';
            }
        });
    </script>
</body>
</html>