
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
            const QuantitySelect = document.getElementById('QuantitySelect');
            const generateVoiceBtn = document.getElementById('generateVoiceBtn');
            const uniqueID = 'Gen' + Math.floor(10000 + Math.random() * 90000);

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
                                    num_prompts: QuantitySelect.value
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


            // Add this event listener
            generateVoiceBtn.addEventListener('click', async function() {

                const script = scriptText.textContent.trim();
                const isDemoMode = demoModeToggle.checked;
                
                console.log('fetched script:', script);

                if (!script) {
                    alert("Please generate a script first");
                    return;
                }
                
                generateVoiceBtn.disabled = true;
                generateVoiceBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Generating...';
                
                try {
                    if (isDemoMode) {
                        // Demo mode - simulate voice generation
                        alert("Voice generated successfully (demo mode)");
                        const randomString = Math.random().toString(36).substring(2, 8);
                        const filename = `${uniqueID}_${randomString}`;
                        console.log("filenamex",filename)
                        
                        {
                            // Get the filename from the first generated image
                            
                            const response = await fetch('http://localhost:5000/generate-voiceover', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    script: "demoo",
                                    //voice_type: VoiceSelect.value,
                                    save_name: filename
                                })
                            });
                            
                            if (!response.ok) {
                                throw new Error("demo Failed to generate voiceover");
                            }
                            
                            const data = await response.json();
                            alert(`demo Voiceover generated successfully: ${data.message}`);
                        }




                    } else {
                        // Get the filename from the first generated image
                        const firstImage = document.querySelector('.generated-image');
                        //let filename = "default_voice";
                        
                        if (firstImage && firstImage.src) {
                            const urlParts = firstImage.src.split('/');
                            //filename = urlParts[urlParts.length - 1].split('-0.png')[0];
                        }
                        const randomString = Math.random().toString(36).substring(2, 8);
                        const filename = `${uniqueID}_${randomString}`;

                        const response = await fetch('http://localhost:5000/generate-voiceover', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                script: script,
                                //voice_type: VoiceSelect.value,
                                save_name: filename
                            })
                        });
                        
                        if (!response.ok) {
                            throw new Error("Failed to generate voiceover");
                        }
                        
                        const data = await response.json();
                        alert(`Voiceover generated successfully: ${data.message}`);
                    }
                } catch (error) {
                    console.error('Error generating voiceover:', error);
                    alert(error.message || "Failed to generate voiceover");
                } finally {
                    generateVoiceBtn.disabled = false;
                    generateVoiceBtn.innerHTML = '<i class="fas fa-microphone me-2"></i> Generate Voiceover';
                }
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
                        const filename = `${uniqueID}_${randomString}`;
                        
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
                        img.src = `http://localhost//shorts//output//${dateString}//${filename}-0.png`;
                       
                    }
                    
                    img.style.display = 'block';
                    placeholder.style.display = 'none';
                    generateVoiceBtn.style.display = 'inline-block';

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