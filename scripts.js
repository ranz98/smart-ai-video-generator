document.addEventListener('DOMContentLoaded', function() {
    // Generate a unique ID for this session/batch early
    const uniqueID = 'Gen' + Math.floor(10000 + Math.random() * 90000);
    console.log('Session Unique ID:', uniqueID);

    // DOM Elements
    let generatedVoiceoverFilename = null;

    const videoIdea = document.getElementById('videoIdea');
    const generatePromptsBtn = document.getElementById('generatePromptsBtn');
    const generateImagesBtn = document.getElementById('generateImagesBtn');
    const createVideoBtn = document.getElementById('createVideoBtn');
    const exampleBtn = document.getElementById('exampleBtn');
    const arrangeBtn = document.getElementById('arrangeBtn');
    const demoModeToggle = document.getElementById('demoModeToggle');
    const promptsSection = document.getElementById('promptsSection');
    const scriptSection = document.getElementById('scriptSection');
    const scriptText = document.getElementById('scriptText'); // This is now the textarea
    const imagesSection = document.getElementById('imagesSection');
    const promptsContainer = document.getElementById('promptsContainer');
    const imageGrid = document.getElementById('imageGrid'); // We'll add listener here
    const styleSelect = document.getElementById('styleSelect');
    const performanceSelect = document.getElementById('performanceSelect');
    const aspectRatioSelect = document.getElementById('aspectRatioSelect');
    const QuantitySelect = document.getElementById('QuantitySelect');
    const generateVoiceBtn = document.getElementById('generateVoiceBtn');
    const saveScriptBtn = document.getElementById('saveScriptBtn'); // <<< Get reference to the new button

    // NEW: Add references for video preview elements
    const videoPreviewSection = document.getElementById('videoPreviewSection');
    const videoPreviewElement = document.getElementById('videoPreviewElement');
    const downloadVideoLink = document.getElementById('downloadVideoLink'); // Get download link


    // API Endpoints
    const PROMPT_GENERATION_API = 'http://localhost:5000/generate-prompts';
    const SCRIPT_GENERATION_API = 'http://localhost:5000/generate-script';
    // NOTE: Image API URL should likely point to the same server as Flask if serving from there
    // but keeping the original for now based on your provided code:
    const IMAGE_GENERATION_API = 'http://127.0.0.1:8888/v1/generation/text-to-image';
    const VOICEOVER_GENERATION_API = 'http://localhost:5000/generate-voiceover'; // Added API URL const
    const VIDEO_CREATION_API = 'http://localhost:5000/create-video';


    // --- Event Listeners ---

    // Example button
    exampleBtn.addEventListener('click', function() {
        videoIdea.value = "5 most beautiful waterfalls around the world";
    });

    // Generate prompts and script button
    generatePromptsBtn.addEventListener('click', async function() {
        const idea = videoIdea.value.trim();
        const isDemoMode = demoModeToggle.checked;

        if (!idea) {
            alert("Please enter a video idea"); // TODO: Replace with better feedback
            return;
        }

        // Show loading state
        generatePromptsBtn.disabled = true;
        generatePromptsBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Generating...';

        // Hide previous results including the video preview
        scriptSection.style.display = 'none';
        promptsSection.style.display = 'none';
        imagesSection.style.display = 'none';
        createVideoBtn.style.display = 'none';
        saveScriptBtn.style.display = 'none';
        videoPreviewSection.style.display = 'none'; // NEW: Hide video preview
        videoPreviewElement.src = ''; // NEW: Clear video source
        downloadVideoLink.style.display = 'none'; // NEW: Hide download link


        try {
            let prompts = [];
            let script = "";

            if (isDemoMode) {
                console.log("Demo Mode: Generating prompts and script.");
                // Use demo data
                prompts = [
                    "A breathtaking view of Niagara Falls from the Canadian side with rainbow in the mist",
                    "Angel Falls in Venezuela cascading down the tabletop mountain",
                    "Iguazu Falls with its hundreds of cascades surrounded by lush rainforest",
                    "Victoria Falls with its massive curtain of water creating a permanent rainbow",
                    "Plitvice Lakes waterfalls in Croatia with their turquoise waters and lush surroundings"
                ];
                script = "This is a demo script about beautiful waterfalls. You can edit this script directly in this box! For example, you could add more details about each location or change the call to action at the end.";
                // Simulate API delay
                await new Promise(resolve => setTimeout(resolve, 1000));
            } else {
                console.log(`Generating ${QuantitySelect.value} prompts and script for: ${idea}`);
                // Call APIs for real data
                const [promptsResponse, scriptResponse] = await Promise.all([
                    fetch(PROMPT_GENERATION_API, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            video_idea: idea,
                            num_prompts: QuantitySelect.value
                        })
                    }),
                    fetch(SCRIPT_GENERATION_API, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ video_idea: idea })
                    })
                ]);

                if (!promptsResponse.ok || !scriptResponse.ok) {
                    // Attempt to read error body if available
                    let errorDetails = "Failed to fetch data from API";
                    try {
                        const errorData = await (promptsResponse.ok ? scriptResponse : promptsResponse).json();
                        errorDetails = errorData.details || errorDetails;
                    } catch (e) {
                        // Ignore JSON parsing error if response wasn't JSON
                    }
                    throw new Error(errorDetails);
                }

                const promptsData = await promptsResponse.json();
                const scriptData = await scriptResponse.json();

                prompts = promptsData.prompts || [];
                script = scriptData.script || "";
                console.log("Generated Prompts:", prompts);
                console.log("Generated Script:", script);
            }

            if (prompts.length === 0) {
                throw new Error("No prompts were generated. Try a different idea.");
            }

            if (!script) {
                throw new Error("No script was generated. Try a different idea.");
            }

            // Display prompts and script
            displayPrompts(prompts);
            scriptText.value = script; // <<< Set value for textarea

            // Show sections
            promptsSection.style.display = 'block';
            scriptSection.style.display = 'block';
            generateVoiceBtn.style.display = 'inline-block'; // Show voice button


        } catch (error) {
            console.error('Error generating content:', error);
            alert(error.message || "Failed to generate content. Check console for details."); // TODO: Replace with better feedback
        } finally {
            // Reset button
            generatePromptsBtn.disabled = false;
            generatePromptsBtn.innerHTML = '<i class="fas fa-bolt me-2"></i> Generate Prompts & Script';
        }
    });

    // Add listener to script textarea to show save button on input
    scriptText.addEventListener('input', function() {
        saveScriptBtn.style.display = 'inline-block';
    });

    // Add listener to save script button
    saveScriptBtn.addEventListener('click', function() {
        const updatedScript = scriptText.value.trim();
        console.log("Script changes saved:", updatedScript); // Placeholder feedback

        // TODO: In a real app, you might want to save this updatedScript
        // to a variable or state management system if other parts of the app
        // need to access the 'official' current script without reading the DOM directly.
        // For now, subsequent steps (voiceover, video) will read directly from scriptText.value

        // Hide save button after saving
        saveScriptBtn.style.display = 'none';
        // TODO: Add a temporary visual confirmation to the user (e.g., "Saved!")
    });


    // Generate images button
    generateImagesBtn.addEventListener('click', async function() {
        const isDemoMode = demoModeToggle.checked;
        // Get all prompts - Read from the displayed prompt elements
        const promptElements = document.querySelectorAll('.prompt-item');
        // Extract just the text content, removing the leading number and dot
        const prompts = Array.from(promptElements).map(el => el.querySelector('.prompt-text').textContent.trim().replace(/^\d+\.\s*/, ''));


        if (prompts.length === 0) {
            alert("No prompts to generate"); // TODO: Replace with better feedback
            return;
        }

        // Show loading state
        generateImagesBtn.disabled = true;
        generateImagesBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Generating...';

        // Clear previous images and hide create video button AND video preview
        imageGrid.innerHTML = '';
        createVideoBtn.style.display = 'none';
        videoPreviewSection.style.display = 'none'; // NEW: Hide video preview
        videoPreviewElement.src = ''; // NEW: Clear video source
        downloadVideoLink.style.display = 'none'; // NEW: Hide download link


        // Show images section
        imagesSection.style.display = 'block';

        // Array to hold promises for initial image generation
        const generationPromises = [];

        // Create image containers with placeholders, regenerate buttons, and start generation
        console.log(`Creating containers and starting generation for ${prompts.length} images...`);
        for (let i = 0; i < prompts.length; i++) {
            const prompt = prompts[i]; // Get the specific prompt for this index
            const container = document.createElement('div');
            container.className = 'image-container';
            // Add a data-index attribute to the container for easier lookup by event delegation
            container.dataset.index = i;

            // --- Generate filename ONCE here when creating the container ---
            const randomString = Math.random().toString(36).substring(2, 8);
            const imageNumber = i + 1;
            // Filename format: Gen[uniqueID]_[random]_[sequence]-0.png
            const filename = `${uniqueID}_${randomString}_${imageNumber}-0`; // Initial filename base for this slot (backend adds .png)


            container.innerHTML = `
                <div class="image-placeholder">
                    <i class="fas fa-image"></i>
                    <small>Generating image ${imageNumber}</small>
                </div>
                <img src="" alt="${prompt}" class="generated-image" data-prompt="${prompt}" data-filename="${filename}">
                <div class="prompt-display">${prompt}</div>
                <button class="prompt-toggle" title="Toggle prompt"><i class="fas fa-comment"></i></button>
                <button class="regenerate-image-btn" title="Regenerate this image" style="display: none;"> <i class="fas fa-sync-alt"></i>
                </button>
            `;
            imageGrid.appendChild(container);

            // Start generation for this image and add the promise to the array
            // Pass the generated filename base to the generateImage function
            generationPromises.push(generateImage(prompt, i, isDemoMode, filename)); // <<< Pass the generated filename base
        }


        try {
            // Use Promise.allSettled to wait for all promises regardless of success/failure
            const results = await Promise.allSettled(generationPromises);
            console.log("Image generation batch finished.", results);

            // Check how many images successfully loaded to decide whether to show the "Create Video" button
            const generatedImages = document.querySelectorAll('.image-container img[style*="display: block"]'); // Count successfully *displayed* images
            const totalContainers = document.querySelectorAll('.image-container').length;

            if (generatedImages.length > 0 && generatedImages.length === totalContainers) { // All attempted images loaded successfully
                createVideoBtn.style.display = 'inline-block';
                console.log("All images generated and loaded successfully. 'Create Video' button enabled.");
            } else if (generatedImages.length > 0) {
                console.warn(`Some images failed to generate or load (${generatedImages.length}/${totalContainers} successful). 'Create Video' button remains hidden.`);
                 // Optionally, still show create video button if at least one image succeeded
                 // createVideoBtn.style.display = 'inline-block'; // Uncomment if you want to allow partial video creation
            } else {
                console.error("No images were successfully generated or loaded.");
            }


        } catch (error) {
            // This catch block would only be hit if Promise.all (not Settled) was used
            // or if generateImage didn't have its own catch. With Promise.allSettled
            // and catch inside generateImage, this block might not be strictly needed,
            // but good for unexpected errors.
            console.error('An unexpected error occurred during the image generation batch:', error);
            alert("An unexpected error occurred during image generation."); // TODO: Replace with better feedback
        } finally {
            // Reset button
            generateImagesBtn.disabled = false;
            generateImagesBtn.innerHTML = '<i class="fas fa-image me-2"></i> Generate All Images';

            // Set up event listeners on the image grid (for prompt toggle and regenerate)
            setupImageGridListeners();
        }
    });

    // NEW: Function to set up listeners on the image grid (for prompt toggle and regenerate)
    function setupImageGridListeners() {
        // Remove any existing listener first to avoid duplicates if this function is called multiple times
        imageGrid.removeEventListener('click', handleImageGridClick); // Remove by named function reference

        imageGrid.addEventListener('click', handleImageGridClick); // Add the named function listener
    }

    // Named function for image grid click handler for easier removal
    function handleImageGridClick(event) {
        const target = event.target;

        // Handle prompt toggle click
        const promptToggleBtn = target.closest('.prompt-toggle');
        if (promptToggleBtn) {
            const promptDisplay = promptToggleBtn.parentElement.querySelector('.prompt-display');
            // Toggle display based on current state
            if (promptDisplay.style.display === 'none' || promptDisplay.style.display === '') {
                promptDisplay.style.display = 'block';
            } else {
                promptDisplay.style.display = 'none';
            }
            return; // Stop processing event for this click
        }

        // Handle regenerate image button click
        const regenerateBtn = target.closest('.regenerate-image-btn'); // Find the closest button
        if (regenerateBtn && !regenerateBtn.disabled) { // Check if it's the regenerate button and not disabled
            const container = regenerateBtn.parentElement; // Get the image container
            const imgElement = container.querySelector('.generated-image'); // Get the image element
            const prompt = imgElement.dataset.prompt; // Get prompt from data attribute
            const filename = imgElement.dataset.filename; // <<< Get the stored filename base
            const index = parseInt(container.dataset.index, 10); // Get index from data attribute
            const isDemoMode = demoModeToggle.checked; // Get current demo mode state

            if (prompt && index >= 0 && container && filename) { // Ensure prompt, index, container, AND filename base exist
                console.log(`User clicked regenerate for image ${index + 1} (Filename Base: ${filename}) with prompt: "${prompt}"`);
                // Disable button and show spinner - this is done *before* calling generateImage
                regenerateBtn.disabled = true;
                regenerateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                 // Hide prompt display while regenerating
                 const promptDisplay = container.querySelector('.prompt-display');
                 promptDisplay.style.display = 'none';

                // Hide video preview if regenerating any image
                videoPreviewSection.style.display = 'none';
                videoPreviewElement.src = '';
                downloadVideoLink.style.display = 'none';


                // Call generateImage for this specific image, passing the STORED filename base
                generateImage(prompt, index, isDemoMode, filename) // <<< Pass the stored filename base
                    .then(() => {
                        // generateImage handles updating the button state and appearance on success/failure
                        console.log(`Regeneration process finished for image ${index + 1}.`);
                        // After any single image regeneration, the "Create Video" button might need re-evaluation
                        // Check if all images are now loaded/successful
                         const generatedImages = document.querySelectorAll('.image-container img[style*="display: block"]');
                         const totalContainers = document.querySelectorAll('.image-container').length;
                         if (generatedImages.length === totalContainers && totalContainers > 0) {
                             createVideoBtn.style.display = 'inline-block';
                         } else {
                             createVideoBtn.style.display = 'none';
                         }

                    })
                    .catch(err => {
                        // This catch would only trigger if generateImage itself threw an unhandled error
                        console.error(`Error during regeneration process for image ${index + 1}:`, err);
                        // generateImage's own catch/onerror should handle the button and placeholder state.
                        // Ensure button is re-enabled if needed for retry, generateImage should handle the icon.
                        if (regenerateBtn) regenerateBtn.disabled = false;
                    });

            } else {
                 console.warn("Cannot regenerate image: prompt, index, container, or filename base missing, or button disabled.");
            }
            return; // Stop processing event for this click
        }
    }


    // Create video button
    createVideoBtn.addEventListener('click', async function() {
        createVideoBtn.disabled = true;
        createVideoBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Creating Video...';
        createVideoBtn.classList.add('creating-video'); // Add a class for potential styling

        // Hide the video preview before creating a new one
        videoPreviewSection.style.display = 'none'; // NEW: Hide video preview
        videoPreviewElement.src = ''; // NEW: Clear video source
        downloadVideoLink.style.display = 'none'; // NEW: Hide download link


        // Get the potentially edited script
        const finalScript = scriptText.value.trim(); // <<< Get script value

        // Get all successfully loaded image filenames (base) in their current order
        // We get filenames from data-filename attribute (which stores the base name)
        const imageFilenamesBase = Array.from(document.querySelectorAll('.image-container img[style*="display: block"]'))
            .filter(img => img.src && img.dataset.filename) // Ensure image is displayed and has filename base data
            .map(img => img.dataset.filename);


        // Check if we have images and a voiceover
        if (imageFilenamesBase.length === 0) {
            alert("No images available to create video. Please generate images first."); // TODO: Replace with better feedback
            createVideoBtn.disabled = false;
            createVideoBtn.innerHTML = '<i class="fas fa-film me-2"></i> Create YouTube Short';
            createVideoBtn.classList.remove('creating-video');
            return;
        }

        if (!generatedVoiceoverFilename) {
            alert("No voiceover available. Please generate voiceover first."); // TODO: Replace with better feedback
            createVideoBtn.disabled = false;
            createVideoBtn.innerHTML = '<i class="fas fa-film me-2"></i> Create YouTube Short';
            createVideoBtn.classList.remove('creating-video');
            return;
        }


        console.log(`Attempting to create video for UniqueID: ${uniqueID}`);
        console.log("Using script:", finalScript);
        // The backend will find images based on the uniqueID, it doesn't need the list of filenames from here for *creation*
        // But it does need the unique_id to find the correct images and voiceover.
        // console.log("Using image filenames (base) (in order):", imageFilenamesBase); // Not sent to backend /create-video
        console.log("Using voiceover file (name stored):", generatedVoiceoverFilename);


        // --- Call backend API to create video ---
        try {
            const response = await fetch(VIDEO_CREATION_API, { // Use the new API URL
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    unique_id: uniqueID, // Pass the unique ID
                    // You might also pass the desired speed multiplier here if you add a setting for it
                    // speed_multiplier: speedSelect.value, // Example if added
                })
            });

            if (!response.ok) {
                 // Attempt to read error body if available
                let errorDetails = `Video creation API failed with status ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorDetails = errorData.details || JSON.stringify(errorData);
                } catch (e) {}
                throw new Error(`Video creation failed: ${response.status} - ${errorDetails}`);
            }

            const data = await response.json();

            if (data.success) {
                alert(`Video created successfully!`); // TODO: Replace with better feedback (maybe remove alert)
                console.log("Video creation responsexxx:", data);
                // NEW: Display the video preview using the working image URL structure
                console.log("trying to showw the videooo:", data);

                    const today = new Date();
                    const dateString = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

                    // Construct the URL using the same pattern that works for images
                    // Note: Using single slashes as is standard for URLs. Double slashes might be a copy/paste artifact.
                    const constructed_video_url = `http://localhost/shorts/output/${dateString}/${data.video_filename}`;

                    videoPreviewElement.src = constructed_video_url; // Set the video source
                    videoPreviewSection.style.display = 'block'; // Show the preview section
                    console.log(`Video preview set to: ${constructed_video_url}`);

                    // NEW: Set download link (optional but helpful)
                    downloadVideoLink.href = constructed_video_url; // Use the constructed URL for download
                    downloadVideoLink.download = data.video_filename; // Suggest filename for download
                    downloadVideoLink.style.display = 'inline-block'; // Show download link

             
                    console.log(`Video preview set to: ${data.video_url}`);

                
                        downloadVideoLink.href = data.video_url; // Use the video URL for download
                        downloadVideoLink.download = data.video_filename; // Suggest filename for download
                        downloadVideoLink.style.display = 'inline-block'; // Show download link
                  
                


            } else {
                // This path is hit if API returns { success: false, ... }
                alert(`Video creation reported failure: ${data.message || 'Unknown error'}`); // TODO: Replace with better feedback
                console.error("Video creation reported failure:", data);
                 // Ensure preview is hidden on failure
                videoPreviewSection.style.display = 'none';
                videoPreviewElement.src = '';
                downloadVideoLink.style.display = 'none';

            }

        } catch (error) {
            console.error('Error during video creation API call:', error);
            alert(error.message || "Failed to create video. Check console for details."); // TODO: Replace with better feedback
            // Ensure preview is hidden on API error
            videoPreviewSection.style.display = 'none';
            videoPreviewElement.src = '';
            downloadVideoLink.style.display = 'none';

        } finally {
            // Reset button regardless of success/failure
            createVideoBtn.disabled = false;
            createVideoBtn.innerHTML = '<i class="fas fa-film me-2"></i> Create YouTube Short';
            createVideoBtn.classList.remove('creating-video');
        }
    });

    // Re-arrange button
    // When rearranging, you should update the data-index of each container to match its new position in the grid's children.
    arrangeBtn.addEventListener('click', function() {
        const containers = Array.from(document.querySelectorAll('.image-container'));
         // Simple shuffle algorithm
        for (let i = containers.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [containers[i], containers[j]] = [containers[j], containers[i]];
        }
        // Append shuffled containers back to the grid AND update their data-index
        containers.forEach((container, newIndex) => {
             container.dataset.index = newIndex; // Update data-index
             imageGrid.appendChild(container);
         });
        console.log("Images re-arranged and data-index updated.");
        // Note: Re-arranging images visually does NOT change the order of prompts in the prompts list.
        // The video creation logic currently just uses the images in the order they appear in the grid.
        // This assumes the voiceover script segments align with the *visual* order of images after shuffling.

        // If images are re-arranged, the previously generated video is no longer valid for this arrangement.
        // Hide the video preview.
        videoPreviewSection.style.display = 'none'; // NEW: Hide video preview
        videoPreviewElement.src = ''; // NEW: Clear video source
        downloadVideoLink.style.display = 'none'; // NEW: Hide download link

        // Re-evaluate if the 'Create Video' button should be shown
        // It should still be shown if all images were successfully loaded before re-arranging.
        const generatedImages = document.querySelectorAll('.image-container img[style*="display: block"]');
        const totalContainers = document.querySelectorAll('.image-container').length;
        if (generatedImages.length === totalContainers && totalContainers > 0) {
             createVideoBtn.style.display = 'inline-block';
        } else {
             createVideoBtn.style.display = 'none';
        }
    });


    // Generate Voiceover button
    generateVoiceBtn.addEventListener('click', async function() {

        const script = scriptText.value.trim(); // <<< Get value from textarea

        console.log('Generating voiceover for script:', script);

        if (!script) {
            alert("Please generate or write a script first"); // TODO: Replace with better feedback
            return;
        }

        // Reset stored voiceover filename
        generatedVoiceoverFilename = null; // Clear previous filename

        generateVoiceBtn.disabled = true;
        generateVoiceBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Generating...';
        saveScriptBtn.disabled = true; // Disable save button while generating voice

        // Hide video preview if generating new voiceover
        videoPreviewSection.style.display = 'none'; // NEW: Hide video preview
        videoPreviewElement.src = ''; // NEW: Clear video source
        downloadVideoLink.style.display = 'none'; // NEW: Hide download link
        // Re-evaluate create video button state (should be hidden until new voiceover is ready)
        createVideoBtn.style.display = 'none';


        try {
            const isDemoMode = demoModeToggle.checked; // Get demo mode state

            if (isDemoMode) {
                // Demo mode - simulate voice generation
                console.log("Simulating voiceover generation (demo mode)");
                const randomString = Math.random().toString(36).substring(2, 8);
                // Filename base for demo voiceover
                const filenameBase = `${uniqueID}_${randomString}_voiceover`;
                const filename = `${filenameBase}.mp3`; // Add .mp3 suffix


                // Simulate a successful API call structure if needed,
                // or just use a timeout and alert
                await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate delay

                generatedVoiceoverFilename = filename; // <<< Store the demo filename (with extension)
                alert("Demo Voiceover generated successfully!"); // TODO: Replace with better feedback + provide playback
                console.log(`Demo voiceover filename: ${generatedVoiceoverFilename}`);


            } else {
                // Real mode - Call backend API
                 const randomString = Math.random().toString(36).substring(2, 8);
                 // Filename base for real voiceover (backend adds .mp3)
                 const filenameBase = `${uniqueID}_${randomString}_voiceover`;
                 // Pass just the base name to backend
                 const filenameToSend = filenameBase;


                const response = await fetch(VOICEOVER_GENERATION_API, { // Use const URL
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        script: script,
                        // voice_type: VoiceSelect.value, // Uncomment if implementing voice type selection
                        save_name: filenameToSend // Send generated filename base
                    })
                });

                if (!response.ok) {
                     // Attempt to read error body
                     let errorDetails = `API request failed with status ${response.status}`;
                     try {
                         const errorData = await response.json();
                         errorDetails = errorData.details || JSON.stringify(errorData);
                     } catch (e) {
                          // Ignore JSON parsing error
                     }
                    throw new Error(`Voiceover API error: ${response.status} - ${errorDetails}`);
                }

                const data = await response.json();
                // Assuming data.filename returned by backend includes the full filename like 'uniqueID_randomstring_voiceover.mp3'
                // Store the full filename returned by the backend
                generatedVoiceoverFilename = data.filename;


                alert(`Voiceover generated successfully: ${data.message}`); // TODO: Replace with better feedback + provide playback
                console.log(`Voiceover generated. File: ${generatedVoiceoverFilename}`);

                // TODO: Add logic here to load/play the audio file using the data.filename
                // You might need a separate backend route to serve voiceover files securely.
                // For now, voiceover filename is just stored for the video creation step.


            }
             // After successful voiceover generation (demo or real), re-evaluate the 'Create Video' button state
             // It should be shown now if images are also ready.
             const generatedImages = document.querySelectorAll('.image-container img[style*="display: block"]');
             const totalContainers = document.querySelectorAll('.image-container').length;
             if (generatedImages.length === totalContainers && totalContainers > 0 && generatedVoiceoverFilename) {
                  createVideoBtn.style.display = 'inline-block';
             } else {
                  createVideoBtn.style.display = 'none';
             }


        } catch (error) {
            console.error('Error generating voiceover:', error);
            alert(error.message || "Failed to generate voiceover. Check console for details."); // TODO: Replace with better feedback
             // Hide create video button on failure
             createVideoBtn.style.display = 'none';

        } finally {
            generateVoiceBtn.disabled = false;
            generateVoiceBtn.innerHTML = '<i class="fas fa-microphone me-2"></i> Generate Voiceover';
            saveScriptBtn.disabled = false; // Re-enable save button
        }
    });

    // --- Helper Functions ---

    // Helper function to display prompts in the prompts container
    function displayPrompts(prompts) {
        promptsContainer.innerHTML = ''; // Clear previous prompts
        prompts.forEach((prompt, index) => {
            const div = document.createElement('div');
            div.className = 'prompt-item';
            div.innerHTML = `
                <span class="prompt-text">${index + 1}. ${prompt}</span>
                <button class="regenerate-prompt" data-index="${index}" title="Regenerate this prompt text">
                    <i class="fas fa-sync-alt"></i>
                </button>
            `;
            promptsContainer.appendChild(div);

            // Add event listener for individual regenerate button
            // This uses direct event listener as prompt items aren't regenerated as a whole grid
             div.querySelector('.regenerate-prompt').addEventListener('click', async function() {
                 const btn = this;
                 const index = parseInt(btn.dataset.index, 10); // Ensure index is parsed

                 // Disable all regenerate buttons temporarily during this operation
                 document.querySelectorAll('.regenerate-prompt').forEach(b => b.disabled = true);
                 btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'; // Show spinner on the button
                 // btn.disabled = true; // Disabled via the loop above


                 await regeneratePrompt(index); // Call the regeneration function

                 // Re-enable all regenerate buttons after regeneration finishes
                 document.querySelectorAll('.regenerate-prompt').forEach(b => {
                      b.disabled = false;
                      // Restore icon only if it's not a spinner or error icon
                      if (!b.innerHTML.includes('fa-spinner') && !b.innerHTML.includes('fa-exclamation-triangle')) {
                           b.innerHTML = '<i class="fas fa-sync-alt"></i>';
                      }
                 });
             });
        });
    }

    // Helper function to regenerate a single prompt text
    async function regeneratePrompt(index) {
        const idea = videoIdea.value.trim();
        if (!idea) {
            alert("Video idea is missing. Cannot regenerate prompt."); // TODO: Better feedback
            return;
        }

        const promptItem = document.querySelectorAll('.prompt-item')[index];
        const regenerateBtn = promptItem.querySelector('.regenerate-prompt'); // Get the specific button

        // Show loading on this specific button (already done in the event listener)
        // regenerateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            let newPrompt = "";
            const isDemoMode = demoModeToggle.checked; // Get demo mode state

            if (isDemoMode) {
                console.log(`Demo Mode: Regenerating prompt ${index + 1}.`);
                // Use demo prompt
                newPrompt = `(Demo Regenerated Prompt) A slightly different angle of the scene for "${videoIdea.value.trim()}" focusing on detail`;
                await new Promise(resolve => setTimeout(resolve, 500)); // Simulate delay

            } else {
                // Call API to regenerate a single prompt
                console.log(`Regenerating prompt text ${index + 1} for idea: ${idea}`);
                const response = await fetch(PROMPT_GENERATION_API, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    // Requesting just 1 prompt, but providing the original idea context
                    body: JSON.stringify({
                        video_idea: idea,
                        num_prompts: 1,
                        // You might enhance your backend API to take the *original* prompt
                        // or index for more targeted regeneration if needed.
                    })
                });

                if (!response.ok) {
                     let errorDetails = `API request failed with status ${response.status}`;
                     try {
                         const errorData = await response.json();
                         errorDetails = errorData.details || JSON.stringify(errorData);
                     } catch (e) {}
                    throw new Error(`Prompt regeneration API error: ${response.status} - ${errorDetails}`);
                }

                const data = await response.json();
                newPrompt = data.prompts?.[0] || "New prompt could not be generated";
                if (newPrompt === "New prompt could not be generated") {
                     console.warn("API generated no prompt string for regeneration.");
                }
            }

            // Update the prompt text while preserving the number
            const promptTextSpan = promptItem.querySelector('.prompt-text');
            const prefix = `${index + 1}. `; // Reconstruct the number prefix
            promptTextSpan.textContent = `${prefix}${newPrompt}`;
            console.log(`Prompt text ${index + 1} regenerated successfully: "${newPrompt}"`);

            // IMPORTANT: Regenerating a prompt text invalidates previously generated images/video.
            // You should hide the images section and the create video button here,
            // forcing the user to regenerate images if they want to use the new prompt.
            imagesSection.style.display = 'none';
            createVideoBtn.style.display = 'none';
            imageGrid.innerHTML = ''; // Clear the image grid
            videoPreviewSection.style.display = 'none'; // NEW: Hide video preview
            videoPreviewElement.src = ''; // NEW: Clear video source
            downloadVideoLink.style.display = 'none'; // NEW: Hide download link

            console.log("Image grid cleared and image/video sections hidden after prompt regeneration.");


        } catch (error) {
            console.error(`Error regenerating prompt ${index + 1}:`, error);
            alert(`Failed to regenerate prompt ${index + 1}.`); // TODO: Better feedback
             regenerateBtn.innerHTML = '<i class="fas fa-exclamation-triangle"></i>'; // Error icon
        } finally {
             // Icon state is managed by the listener loop now.
        }
    }


    // Helper function to generate and display a single image
    // Now accepts the desired filename base as a parameter
    async function generateImage(prompt, index, isDemoMode, filenameBase) { // <<< Added filenameBase parameter
        const containers = document.querySelectorAll('.image-container');
        const container = containers[index]; // Get the correct container based on index
        if (!container) {
             console.error(`Error: Image container not found for index ${index}`);
             return Promise.reject(new Error(`Container not found for index ${index}`)); // Return rejected promise
        }
        const img = container.querySelector('img');
        const placeholder = container.querySelector('.image-placeholder');
        const promptDisplay = container.querySelector('.prompt-display');
        const regenerateBtn = container.querySelector('.regenerate-image-btn'); // Get regenerate button reference

        // Ensure prompt and filename base are set on the image element
        img.dataset.prompt = prompt;
        img.dataset.filename = filenameBase; // Make sure filename base is stored


        // Show loading state
        placeholder.innerHTML = '<i class="fas fa-spinner fa-spin"></i><small>Generating...</small>';
        placeholder.style.display = 'flex'; // Ensure placeholder is visible
        img.style.display = 'none'; // Ensure image is hidden initially
        promptDisplay.style.display = 'none'; // Hide prompt overlay during generation
        // Hide any existing retry button in the placeholder
         placeholder.querySelectorAll('.btn.btn-sm').forEach(btn => btn.remove());

        if(regenerateBtn) { // Hide and disable regenerate button during generation
             regenerateBtn.style.display = 'none';
             regenerateBtn.disabled = true;
        }

         // imageNumber is only used for display/logging now, not filename construction
         const imageNumber = index + 1;

        try {
            if (isDemoMode) {
                console.log(`Demo Mode: Generating image ${imageNumber} for prompt: "${prompt}" (Filename Base: ${filenameBase})`);
                // Use demo image URL
                 const unsplashKeyword = encodeURIComponent(prompt.split(' ')[0] || 'abstract'); // Use first word or 'abstract'
                 const timestamp = new Date().getTime(); // <<< Get current timestamp
                 // Still use index/number for potential variety in demo image URL
                 // Demo mode uses Unsplash, the filenameBase is not used for the source URL, but stored for potential future use
                 img.src = `https://source.unsplash.com/random/704x1408/?${unsplashKeyword}&sig=${imageNumber}&t=${timestamp}`; // <<< Append timestamp
                 // Simulate API delay before loading the image
                 await new Promise(resolve => setTimeout(resolve, 800));

                 console.log(`Demo image generation simulated for image ${imageNumber}. Loading...`);
                 // Display logic is handled by img.onload/onerror callbacks attached below

            } else {
                // Real mode - Use the filename base provided as a parameter
                 console.log(`Attempting real image generation for prompt ${imageNumber} with save_name base: ${filenameBase}`);

                 const response = await fetch(IMAGE_GENERATION_API, {
                     method: 'POST',
                     headers: { 'Content-Type': 'application/json' },
                     body: JSON.stringify({
                         prompt: prompt,
                         style_selections: [styleSelect.value],
                         performance_selection: performanceSelect.value,
                         aspect_ratios_selection: aspectRatioSelect.value,
                         save_name: filenameBase // <<< USE THE PROVIDED FILENAME BASE (backend adds extension like -0.png)
                     })
                 });

                 if (!response.ok) {
                      let errorDetails = `API request failed with status ${response.status}`;
                      try {
                          const errorData = await response.json();
                           errorDetails = errorData.detail || errorData.details || JSON.stringify(errorData);
                      } catch (e) {}
                     throw new Error(`Image generation API error: ${response.status} - ${errorDetails}`);
                 }
                 // API call was successful, now wait for the image file to be accessible and load in the browser

                 const today = new Date();
                 const dateString = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

                 // Construct the image URL using the PROVIDED filename base + expected suffix + date
                 // The backend saves as filenameBase-0.png, frontend needs to request that specific file
                 let imageUrl = `http://localhost/shorts/output/${dateString}/${filenameBase}-0.png`; // Base URL

                 // Append a cache-busting timestamp
                 const timestamp = new Date().getTime(); // <<< Get current timestamp
                 imageUrl = `${imageUrl}?t=${timestamp}`; // <<< Append timestamp

                 img.src = imageUrl; // Set the modified URL
                 console.log(`Image URL constructed with cache buster: ${img.src}`);

                 // Wait for the image element to successfully load the src
                 // Clear previous onload/onerror handlers to avoid duplicates
                 img.onload = null;
                 img.onerror = null;
                 await new Promise((resolve, reject) => {
                      img.onload = resolve;
                      img.onerror = reject;
                      // Optional: Add a timeout
                      // setTimeout(() => reject(new Error("Image loading timed out")), 30000); // e.g., 30 seconds
                 });

                 console.log(`Image ${imageNumber} loaded successfully from URL: ${img.src}`);

            } // End of else (real mode)

             // --- Actions after successful generation API call AND successful image loading ---
             img.style.display = 'block'; // Show the image
             placeholder.style.display = 'none'; // Hide the placeholder
             promptDisplay.textContent = prompt; // Set the prompt text in the overlay
             // promptDisplay.style.display = 'block'; // Optional: show prompt by default
             if(regenerateBtn) { // Show and enable regenerate button
                  regenerateBtn.style.display = 'flex';
                  regenerateBtn.innerHTML = '<i class="fas fa-sync-alt"></i>'; // Sync icon
                  regenerateBtn.disabled = false;
             }

            // After any single image regeneration/success, ensure the video preview is hidden
            videoPreviewSection.style.display = 'none'; // NEW: Hide video preview
            videoPreviewElement.src = ''; // NEW: Clear video source
            downloadVideoLink.style.display = 'none'; // NEW: Hide download link


             return Promise.resolve(); // Resolve the promise for Promise.allSettled


        } catch (error) {
            console.error(`Error during generateImage process for image ${imageNumber} (Filename Base: ${filenameBase}):`, error);
            placeholder.innerHTML = '<i class="fas fa-exclamation-triangle"></i><small>Generation failed</small>';
            placeholder.style.display = 'flex';
            img.style.display = 'none';
            promptDisplay.style.display = 'none';

            if(regenerateBtn) { // Show and enable regenerate button on error
                 regenerateBtn.style.display = 'flex';
                 regenerateBtn.innerHTML = '<i class="fas fa-sync-alt"></i>'; // Or retry icon
                 regenerateBtn.disabled = false;
            }
            // Add retry button to placeholder (if not already there)
            if (!placeholder.querySelector('.btn.btn-sm')) {
                 const retryBtn = document.createElement('button');
                 retryBtn.className = 'btn btn-sm btn-outline-secondary mt-2';
                 retryBtn.innerHTML = '<i class="fas fa-redo"></i> Retry';
                 // Call generateImage with the same parameters including filename base
                 // This call will also apply the cache buster
                 retryBtn.addEventListener('click', () => generateImage(prompt, index, isDemoMode, filenameBase));
                 placeholder.appendChild(retryBtn);
            }

            // After any single image regeneration failure, ensure the video preview is hidden
            videoPreviewSection.style.display = 'none'; // NEW: Hide video preview
            videoPreviewElement.src = ''; // NEW: Clear video source
            downloadVideoLink.style.display = 'none'; // NEW: Hide download link


            return Promise.reject(error); // Reject the promise for Promise.allSettled
        }
         // No final block needed here as try/catch/return handles promise outcome
    }
});