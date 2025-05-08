<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Shorts Creator</title>
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
            min-height: 100px;
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

        .error-message {
            color: #ff6b6b;
            display: none;
            margin-top: 10px;
        }

        .status-message {
            margin-top: 10px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        /* Image grid styles - 6 columns */
        .image-grid {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 15px;
            margin-top: 20px;
        }

        .image-container {
            position: relative;
            background-color: rgba(255, 255, 255, 0.03);
            border: 2px dashed rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            aspect-ratio: 9/16;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        .image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: none;
        }

        .image-placeholder {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: var(--text-secondary);
        }

        .image-placeholder i {
            font-size: 2rem;
            margin-bottom: 10px;
        }

        .prompt-display {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
            padding: 10px;
            font-size: 0.8rem;
            color: white;
            display: none;
        }

        .prompt-toggle {
            position: absolute;
            top: 5px;
            right: 5px;
            background: rgba(0,0,0,0.5);
            border: none;
            color: white;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }

        /* Demo mode toggle */
        .demo-toggle {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }

        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 30px;
        }

        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 22px;
            width: 22px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background-color: var(--accent-color);
        }

        input:checked + .slider:before {
            transform: translateX(30px);
        }

        /* Script section */
        .script-container {
            background-color: var(--card-dark);
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            max-height: 300px;
            overflow-y: auto;
        }

        .script-text {
            white-space: pre-wrap;
            font-family: monospace;
        }

        /* Wider prompts container */
        .col-lg-8 {
            flex: 0 0 80%;
            max-width: 80%;
        }

        .col-lg-4 {
            flex: 0 0 20%;
            max-width: 20%;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fab fa-youtube me-2"></i>YouTube Shorts Creator
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="#"><i class="fas fa-history me-1"></i> History</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container py-4">
        <div class="main-container">
            <div class="row">
                <div class="col-lg-8">
                    <div class="demo-toggle">
                        <span>Demo Mode:</span>
                        <label class="toggle-switch">
                            <input type="checkbox" id="demoModeToggle">
                            <span class="slider"></span>
                        </label>
                    </div>

                    <div class="prompt-card p-4 mb-4">
                        <h5 class="mb-3"><i class="fas fa-lightbulb me-2"></i>Video Idea</h5>
                        <textarea class="form-control prompt-textarea mb-3" id="videoIdea" placeholder="Enter your YouTube Shorts video idea (e.g., '5 beautiful waterfalls around the world')"></textarea>
                        <div class="d-flex justify-content-between align-items-center">
                            <button class="btn btn-sm btn-outline-secondary" id="exampleBtn">
                                <i class="fas fa-question-circle me-1"></i> Show Example
                            </button>
                            <button class="btn btn-generate" id="generatePromptsBtn">
                                <i class="fas fa-bolt me-2"></i> Generate Prompts & Script
                            </button>
                        </div>
                    </div>

                    <div id="scriptSection" style="display: none;">
                        <h5 class="text-white mb-3"><i class="fas fa-scroll me-2"></i>Generated Script</h5>
                        <div class="script-container">
                            <pre class="script-text" id="scriptText"></pre>
                        </div>
                    </div>

                    <div id="promptsSection" style="display: none;">
                        <h5 class="text-white mb-3"><i class="fas fa-list-ol me-2"></i>Generated Prompts</h5>
                        <div class="prompt-card p-4 mb-4">
                            <div id="promptsContainer"></div>
                            <div class="d-flex justify-content-end mt-3">
                                <button class="btn btn-generate" id="generateImagesBtn">
                                    <i class="fas fa-image me-2"></i> Generate All Images
                                </button>
                            </div>
                        </div>
                    </div>

                    <div id="imagesSection" style="display: none;">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="text-white mb-0"><i class="fas fa-images me-2"></i>Generated Images</h5>
                            <button class="btn btn-sm btn-outline-secondary" id="arrangeBtn">
                                <i class="fas fa-random me-1"></i> Re-arrange
                            </button>
                        </div>
                        <div class="image-grid" id="imageGrid"></div>
                        <div class="d-flex justify-content-center mt-4">
                            <button class="btn btn-generate" id="createVideoBtn" style="display: none;">
                                <i class="fas fa-film me-2"></i> Create YouTube Short
                            </button>
                        </div>
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
                                <option value="704*1408" selected>704×1408 (Shorts Vertical)</option>
                                <option value="768*1344">768×1344 (Landscape)</option>
                                <option value="1024*1024">1024×1024 (Square)</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="footer text-center py-3">
        <div class="container">
            <p class="mb-0">© 2023 YouTube Shorts Creator | Powered by AI</p>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // DOM Elements
            const videoIdea = document.getElementById('videoIdea');
            const generatePromptsBtn = document.getElementById('generatePromptsBtn');
            const generateImagesBtn = document.getElementById('generateImagesBtn');
            const createVideoBtn = document.getElementById('createVideoBtn');
            const exampleBtn = document.getElementById('exampleBtn');
            const arrangeBtn = document.getElementById('arrangeBtn');
            const demoModeToggle = document.getElementById('demoModeToggle');
            const promptsSection = document.getElementById('promptsSection');
            const scriptSection = document.getElementById('scriptSection');
            const scriptText = document.getElementById('scriptText');
            const imagesSection = document.getElementById('imagesSection');
            const promptsContainer = document.getElementById('promptsContainer');
            const imageGrid = document.getElementById('imageGrid');
            const styleSelect = document.getElementById('styleSelect');
            const performanceSelect = document.getElementById('performanceSelect');
            const aspectRatioSelect = document.getElementById('aspectRatioSelect');

            // API Endpoints
            const PROMPT_GENERATION_API = 'http://localhost:5000/generate-prompts';
            const SCRIPT_GENERATION_API = 'http://localhost:5000/generate-script';
            const IMAGE_GENERATION_API = 'http://127.0.0.1:8888/v1/generation/text-to-image';

            // Example button
            exampleBtn.addEventListener('click', function() {
                videoIdea.value = "5 most beautiful waterfalls in the world";
            });

            // Generate prompts and script button
            generatePromptsBtn.addEventListener('click', async function() {
                const idea = videoIdea.value.trim();
                const isDemoMode = demoModeToggle.checked;
                
                if (!idea) {
                    alert("Please enter a video idea");
                    return;
                }
                
                // Show loading state
                generatePromptsBtn.disabled = true;
                generatePromptsBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Generating...';
                
                try {
                    let prompts = [];
                    let script = "";
                    
                    if (isDemoMode) {
                        // Use demo data
                        prompts = [
                            "A breathtaking view of Niagara Falls from the Canadian side with rainbow in the mist",
                            "Angel Falls in Venezuela cascading down the tabletop mountain",
                            "Iguazu Falls with its hundreds of cascades surrounded by lush rainforest",
                            "Victoria Falls with its massive curtain of water creating a permanent rainbow",
                            "Plitvice Lakes waterfalls in Croatia with their turquoise waters and lush surroundings"
                        ];
                        script = "Demo script:\n\n1. Introduction to the world's most beautiful waterfalls\n2. Showcase each waterfall with interesting facts\n3. Closing thoughts and call to action";
                    } else {
                        // Call APIs for real data
                        const [promptsResponse, scriptResponse] = await Promise.all([
                            fetch(PROMPT_GENERATION_API, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    video_idea: idea,
                                    num_prompts: 5
                                })
                            }),
                            fetch(SCRIPT_GENERATION_API, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    video_idea: idea
                                })
                            })
                        ]);
                        
                        if (!promptsResponse.ok || !scriptResponse.ok) {
                            throw new Error("Failed to fetch data from API");
                        }
                        
                        const promptsData = await promptsResponse.json();
                        const scriptData = await scriptResponse.json();
                        
                        prompts = promptsData.prompts || [];
                        script = scriptData.script || "";
                    }
                    
                    if (prompts.length === 0) {
                        throw new Error("No prompts were generated");
                    }
                    
                    // Display prompts and script
                    displayPrompts(prompts);
                    scriptText.textContent = script;
                    
                    // Show sections
                    promptsSection.style.display = 'block';
                    scriptSection.style.display = 'block';
                    
                } catch (error) {
                    console.error('Error generating content:', error);
                    alert(error.message || "Failed to generate content");
                } finally {
                    // Reset button
                    generatePromptsBtn.disabled = false;
                    generatePromptsBtn.innerHTML = '<i class="fas fa-bolt me-2"></i> Generate Prompts & Script';
                }
            });

            // Generate images button
            generateImagesBtn.addEventListener('click', async function() {
                const isDemoMode = demoModeToggle.checked;
                // Get all prompts
                const promptElements = document.querySelectorAll('.prompt-item');
                const prompts = Array.from(promptElements).map(el => el.querySelector('.prompt-text').textContent.trim());
                
                if (prompts.length === 0) {
                    alert("No prompts to generate");
                    return;
                }
                
                // Show loading state
                generateImagesBtn.disabled = true;
                generateImagesBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Generating...';
                
                // Clear previous images
                imageGrid.innerHTML = '';
                
                // Create image containers
                for (let i = 0; i < prompts.length; i++) {
                    const container = document.createElement('div');
                    container.className = 'image-container';
                    container.innerHTML = `
                        <div class="image-placeholder">
                            <i class="fas fa-image"></i>
                            <small>Generating image ${i+1}</small>
                        </div>
                        <img src="" alt="${prompts[i]}" class="generated-image" data-prompt="${prompts[i]}">
                        <div class="prompt-display">${prompts[i]}</div>
                        <button class="prompt-toggle" title="Toggle prompt"><i class="fas fa-comment"></i></button>
                    `;
                    imageGrid.appendChild(container);
                }
                
                // Show images section
                imagesSection.style.display = 'block';
                
                // Generate images in parallel
                const generationPromises = prompts.map((prompt, index) => 
                    generateImage(prompt, index, isDemoMode)
                );
                
                try {
                    await Promise.all(generationPromises);
                    // Enable create video button
                    createVideoBtn.style.display = 'inline-block';
                } catch (error) {
                    console.error('Error generating images:', error);
                    alert("Some images failed to generate. Please try again.");
                } finally {
                    // Reset button
                    generateImagesBtn.disabled = false;
                    generateImagesBtn.innerHTML = '<i class="fas fa-image me-2"></i> Generate All Images';
                    
                    // Add event listeners for prompt toggles
                    document.querySelectorAll('.prompt-toggle').forEach(btn => {
                        btn.addEventListener('click', function() {
                            const promptDisplay = this.parentElement.querySelector('.prompt-display');
                            promptDisplay.style.display = promptDisplay.style.display === 'none' ? 'block' : 'none';
                        });
                    });
                }
            });

            // Create video button
            createVideoBtn.addEventListener('click', function() {
                createVideoBtn.disabled = true;
                createVideoBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Creating Video...';
                createVideoBtn.classList.add('creating-video');
                
                // Get all generated images
                const images = Array.from(document.querySelectorAll('.generated-image'))
                    .filter(img => img.style.display === 'block')
                    .map(img => ({
                        src: img.src,
                        prompt: img.dataset.prompt
                    }));
                
                if (images.length === 0) {
                    alert("No images available to create video");
                    createVideoBtn.disabled = false;
                    createVideoBtn.innerHTML = '<i class="fas fa-film me-2"></i> Create YouTube Short';
                    createVideoBtn.classList.remove('creating-video');
                    return;
                }
                
                // Simulate video creation
                setTimeout(() => {
                    alert("Video created successfully! (This would export a video file in a real implementation)");
                    createVideoBtn.disabled = false;
                    createVideoBtn.innerHTML = '<i class="fas fa-film me-2"></i> Create YouTube Short';
                    createVideoBtn.classList.remove('creating-video');
                }, 3000);
            });

            // Re-arrange button
            arrangeBtn.addEventListener('click', function() {
                const containers = Array.from(document.querySelectorAll('.image-container'));
                for (let i = containers.length - 1; i > 0; i--) {
                    const j = Math.floor(Math.random() * (i + 1));
                    [containers[i], containers[j]] = [containers[j], containers[i]];
                }
                containers.forEach(container => imageGrid.appendChild(container));
            });

            // Helper functions
            function displayPrompts(prompts) {
                promptsContainer.innerHTML = '';
                prompts.forEach((prompt, index) => {
                    const div = document.createElement('div');
                    div.className = 'prompt-item';
                    div.innerHTML = `
                        <span class="prompt-text">${index + 1}. ${prompt}</span>
                        <button class="regenerate-prompt" data-index="${index}" title="Regenerate this prompt">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    `;
                    promptsContainer.appendChild(div);
                    
                    // Add event listener for regenerate button
                    div.querySelector('.regenerate-prompt').addEventListener('click', async function() {
                        await regeneratePrompt(index);
                    });
                });
            }

            async function regeneratePrompt(index) {
                const idea = videoIdea.value.trim();
                if (!idea) return;
                
                const promptItem = document.querySelectorAll('.prompt-item')[index];
                const regenerateBtn = promptItem.querySelector('.regenerate-prompt');
                const isDemoMode = demoModeToggle.checked;
                
                // Show loading
                regenerateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                
                try {
                    let newPrompt = "";
                    
                    if (isDemoMode) {
                        // Use demo prompt
                        newPrompt = "New demo prompt showing a different angle of the location";
                    } else {
                        // Call API to regenerate a single prompt
                        const response = await fetch(PROMPT_GENERATION_API, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                video_idea: idea,
                                num_prompts: 1
                            })
                        });
                        
                        if (!response.ok) {
                            throw new Error(`API request failed with status ${response.status}`);
                        }
                        
                        const data = await response.json();
                        newPrompt = data.prompts?.[0] || "New prompt could not be generated";
                    }
                    
                    // Update the prompt text while preserving the number
                    const promptText = promptItem.querySelector('.prompt-text');
                    const prefix = promptText.textContent.split('.')[0] + '.';
                    promptText.textContent = `${prefix} ${newPrompt}`;
                    
                } catch (error) {
                    console.error('Error regenerating prompt:', error);
                    alert("Failed to regenerate prompt");
                } finally {
                    // Reset button
                    regenerateBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
                }
            }

            async function generateImage(prompt, index, isDemoMode) {
                const containers = document.querySelectorAll('.image-container');
                const container = containers[index];
                const img = container.querySelector('img');
                const placeholder = container.querySelector('.image-placeholder');
                
                // Show loading for this image
                placeholder.innerHTML = '<i class="fas fa-spinner fa-spin"></i><small>Generating...</small>';
                
                try {
                    if (isDemoMode) {
                        // Use demo image
                        img.src = `https://source.unsplash.com/random/768x1344/?${encodeURIComponent(prompt.split(' ')[0])}`;
                    } else {
                        // Generate a random filename
                        const timestamp = new Date().getTime();
                        const randomString = Math.random().toString(36).substring(2, 8);
                        const filename = `generated-${timestamp}-${randomString}`;
                        
                        // Call the image generation API
                        const response = await fetch(IMAGE_GENERATION_API, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                prompt: prompt,
                                style_selections: [styleSelect.value],
                                performance_selection: performanceSelect.value,
                                aspect_ratios_selection: aspectRatioSelect.value,
                                save_name: filename
                            })
                        });
                        
                        if (!response.ok) {
                            throw new Error(`API request failed with status ${response.status}`);
                        }
                        
                        // Get current date in YYYY-MM-DD format for the path
                        const today = new Date();
                        const dateString = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
                        
                        // Construct the image URL
                        img.src = `http://localhost:8009/${filename}-0.png`;
                    }
                    
                    img.style.display = 'block';
                    placeholder.style.display = 'none';
                    
                    // Show the prompt display
                    container.querySelector('.prompt-display').style.display = 'block';
                    
                } catch (error) {
                    console.error('Error generating image:', error);
                    placeholder.innerHTML = '<i class="fas fa-exclamation-triangle"></i><small>Failed to generate</small>';
                    
                    // Retry button
                    const retryBtn = document.createElement('button');
                    retryBtn.className = 'btn btn-sm btn-outline-secondary mt-2';
                    retryBtn.innerHTML = '<i class="fas fa-redo"></i> Retry';
                    retryBtn.addEventListener('click', () => generateImage(prompt, index, isDemoMode));
                    placeholder.appendChild(retryBtn);
                }
            }
        });
    </script>
</body>
</html>