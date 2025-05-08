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

        /* Loading animation */
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

        /* Generated image styling */
        .generated-image {
            max-width: 100%;
            border-radius: 8px;
            display: none;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
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
                                <button class="btn btn-sm btn-outline-secondary me-2">
                                    <i class="fas fa-magic me-1"></i> Enhance
                                </button>
                                <button class="btn btn-sm btn-outline-secondary">
                                    <i class="fas fa-random me-1"></i> Random
                                </button>
                            </div>
                            <span class="text-muted small" id="charCount">0/500</span>
                        </div>
                    </div>

                    <div class="image-placeholder mb-4" id="imagePlaceholder">
                        <i class="fas fa-image fa-3x mb-3"></i>
                        <p>Your generated image will appear here</p>
                        <div class="loader" id="loader"></div>
                        <img src="" alt="Generated Image" class="generated-image" id="generatedImage">
                    </div>
                </div>

                <div class="col-lg-4">
                    <div class="settings-card p-4 mb-4">
                        <h5 class="mb-3"><i class="fas fa-sliders-h me-2"></i>Generation Settings</h5>
                        
                        <div class="mb-3">
                            <label for="modelSelect" class="form-label">Model</label>
                            <select class="form-select" id="modelSelect">
                                <option selected>Stable Diffusion v2.1</option>
                                <option>DALL-E 3</option>
                                <option>Midjourney v5</option>
                                <option>Custom Model</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="styleSelect" class="form-label">Style</label>
                            <select class="form-select" id="styleSelect">
                                <option selected>Realistic</option>
                                <option>Digital Art</option>
                                <option>Fantasy Art</option>
                                <option>Anime</option>
                                <option>Photographic</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="sizeSelect" class="form-label">Image Size</label>
                            <select class="form-select" id="sizeSelect">
                                <option selected>1024x1024</option>
                                <option>512x512</option>
                                <option>768x768</option>
                                <option>1024x768</option>
                            </select>
                        </div>

                        <div class="mb-4">
                            <label for="qualityRange" class="form-label">Quality: <span id="qualityValue">75</span>%</label>
                            <input type="range" class="form-range" min="25" max="100" step="1" id="qualityRange" value="75">
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
                            <button class="btn btn-outline-secondary">
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
            <p class="mb-0">© 2023 AI Image Generator | Powered by AI Magic</p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Character counter for textarea
            const promptInput = document.getElementById('promptInput');
            const charCount = document.getElementById('charCount');
            
            promptInput.addEventListener('input', function() {
                const currentLength = this.value.length;
                charCount.textContent = `${currentLength}/500`;
                
                if (currentLength > 500) {
                    charCount.classList.add('text-danger');
                } else {
                    charCount.classList.remove('text-danger');
                }
            });

            // Quality range value display
            const qualityRange = document.getElementById('qualityRange');
            const qualityValue = document.getElementById('qualityValue');
            
            qualityRange.addEventListener('input', function() {
                qualityValue.textContent = this.value;
            });

            // Generate button functionality
            const generateBtn = document.getElementById('generateBtn');
            const imagePlaceholder = document.getElementById('imagePlaceholder');
            const loader = document.getElementById('loader');
            const generatedImage = document.getElementById('generatedImage');
            
            generateBtn.addEventListener('click', function() {
                if (promptInput.value.trim() === '') {
                    alert('Please enter a description for your image');
                    return;
                }
                
                // Show loading state
                generateBtn.disabled = true;
                generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Generating...';
                loader.style.display = 'block';
                imagePlaceholder.querySelector('i').style.display = 'none';
                imagePlaceholder.querySelector('p').style.display = 'none';
                generatedImage.style.display = 'none';
                
                // Simulate API call with timeout
                setTimeout(function() {
                    // Hide loader and show generated image (simulated)
                    loader.style.display = 'none';
                    
                    // In a real app, you would set the src to the actual generated image URL
                    generatedImage.src = 'https://via.placeholder.com/1024x1024/6e48aa/ffffff?text=Generated+Image';
                    generatedImage.style.display = 'block';
                    
                    // Reset button
                    generateBtn.disabled = false;
                    generateBtn.innerHTML = '<i class="fas fa-bolt me-2"></i> Generate Image';
                }, 3000);
            });
        });
    </script>
</body>
</html>