<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Shorts Creator</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="styles.css">

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
                        <textarea class="form-control script-text" id="scriptText" rows="10" placeholder="Generated script will appear here..."></textarea>

                        <div class="d-flex justify-content-end mt-3">
                            <button class="btn btn-secondary me-2" id="saveScriptBtn" style="display: none;">
                                <i class="fas fa-save me-2"></i> Save Changes
                            </button>
                            <button class="btn btn-generate" id="generateVoiceBtn">
                            <i class="fas fa-microphone me-2"></i> Generate Voiceover
                            </button>
                        </div>
                    </div>
                </div>

                    <div id="promptsSection" style="display: none;">
                        <h5 class="text-white mb-3"><i class="fas fa-list-ol me-2"></i>Generated Prompts</h5>
                        <div class="prompt-card p-4 mb-4">
                            <div id="promptsContainer"></div>
                            <div class="d-flex justify-content-end mt-3">
                                <button class="btn btn-generate" id="generateImagesBtn">
                                    <i class="fas fa-image me-2"></i> Generate All Imagesx
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

                        <div class="mb-3">
                            <label for="QuantitySelect" class="form-label">Quantity</label>
                            <select class="form-select" id="QuantitySelect">
                                <option value="1" selected>1</option>
                                <option value="2">2</option>
                                <option value="3">3</option>
                                <option value="4">4</option>
                                <option value="5">5</option>
                                <option value="10">10</option>
                                <option value="15">15</option>
                            </select>
                        </div>

                        <div class="mb-3">
                            <label for="VoiceSelect" class="form-label">Voice Over</label>
                            <select class="form-select" id="VoiceSelect">
                                <option value="1" selected>1</option>
                                <option value="2">2</option>
                                <option value="3">3</option>
                                <option value="4">4</option>
                                <option value="5">5</option>
                            </select>
                        </div>


                    </div>

                    <div id="videoPreviewSection" class="settings-card p-4 mb-4" style="display: none;">
                        <h5 class="mb-3"><i class="fas fa-video me-2"></i>Video Preview</h5>
                        <video id="videoPreviewElement" controls class="w-100"></video>
                        <div class="mt-3 text-center">
                            <a href="#" id="downloadVideoLink" class="btn btn-secondary btn-sm" download style="display: none;">
                                <i class="fas fa-download me-2"></i> Download Video
                            </a>
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

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="scripts.js"></script>


</body>
</html>