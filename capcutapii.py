import time
import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Page
from datetime import date # Import datetime module
# --- Configuration ---
# Directly navigating to the Text-to-Speech tool page
TTS_TOOL_URL = "https://www.capcut.com/magic-tools/text-to-speech"
PERSISTENT_CONTEXT_PATH = os.path.join(os.path.expanduser("~"), "playwright_capcut_context") # Path to store browser context data
TEXT_TO_GENERATE = "hello" # Text to enter
# Path where files will be downloaded (configured in context options)
today = date.today()
date_str = today.strftime("%Y-%m-%d")
# Construct the download directory path
DOWNLOAD_DIRECTORY = os.path.join("D:\\Program Files\\xampp\\htdocs\\shorts\\output", date_str)

# --- WARNING: STORING CREDENTIALS DIRECTLY IS INSECURE ---
# Replace with your actual CapCut login credentials.
# Consider using environment variables or a secure method in production.
email = "mihinper98@gmail.com" # <<< REPLACE WITH YOUR EMAIL
password = "dulanja@123" # <<< REPLACE WITH YOUR PASSWORD
# --- END WARNING ---


# --- Ensure download directory exists (still good practice) ---
if not os.path.exists(DOWNLOAD_DIRECTORY):
    os.makedirs(DOWNLOAD_DIRECTORY)

# --- Placeholder Selectors (REPLACE WITH ACTUAL SELECTORS) ---
# Use your browser's developer tools (F12) to find the actual selectors
# Selector for the text input area on the TTS page
TEXT_INPUT_SELECTOR = "div.zone-container.editor-kit-container.editor-klZa9E[contenteditable=\"true\"]"
# Selector for the 'Adam' voice option based on the provided class
ADAM_VOICE_SELECTOR = "div.toneItem__name-MfPqhL"
# Selector for the Generate button based on the provided class
GENERATE_BUTTON_SELECTOR = "div.aigc-btn-logo-wrapper-ZtdNWU"
# Selector for the Download button based on the provided classes
DOWNLOAD_BUTTON_SELECTOR = "div.lv-btn.lv-btn-primary.lv-btn-size-default.lv-btn-shape-square.card-item-button-RhMVTy.download-button-ys5iww"
# Selector for the dropdown menu inner element after clicking download (used as a container check)
DOWNLOAD_DROPDOWN_INNER_SELECTOR = "div.lv-dropdown-menu-inner"
# Selector for the 'Audio only' option within the download dropdown
AUDIO_ONLY_MENU_ITEM_SELECTOR = ".lv-dropdown-menu-item:has-text(\"Audio only\")"

# --- Selectors for Login ---
LOGIN_WELCOME_TEXT = "Welcome to capcut" # Text to check for login page
# Updated Selector for email input (using the name attribute of the input tag)
EMAIL_INPUT_SELECTOR = "input[name=\"signUsername\"]"
CONTINUE_BUTTON_SELECTOR = ".lv-btn.lv-btn-primary.lv-btn-size-default.lv-btn-shape-square.lv_sign_in_panel_wide-primary-button" # Selector for continue button
# Selector for password input div (keeping click+type for now)
PASSWORD_INPUT_SELECTOR = "input[type=\"password\"]"
SIGN_IN_BUTTON_SELECTOR = ".lv-btn.lv-btn-primary.lv-btn-size-large.lv-btn-shape-square.lv_sign_in_panel_wide-sign-in-button.lv_sign_in_panel_wide-primary-button" # Selector for sign in button


# --- Separate Function to Enter Text ---
def capcutEnterText(page: Page, text: str):
    """
    Waits for the text input element and enters the specified text.

    Args:
        page: The Playwright Page object representing the current browser tab.
        text: The string of text to enter into the input field.
    """
    print("Attempting to find and interact with the text input field...")
    try:
        # Wait until the text input element is visible on the page
        # The wait before calling this function should handle the modal,
        # but this wait is still good practice.
        page.wait_for_selector(TEXT_INPUT_SELECTOR, state='visible', timeout=30000) # Wait up to 30 seconds for visibility
        print(f"Text input element found using selector: {TEXT_INPUT_SELECTOR}")

        # Click the element to ensure it's focused and ready for typing
        page.click(TEXT_INPUT_SELECTOR)
        print("Clicked the text input field to focus.")

        # Type the specified text into the focused element
        page.keyboard.type(text)
        print(f"Entered text: '{text}'")

    except PlaywrightTimeoutError:
        # Handle timeout specifically if the element doesn't appear
        print(f"Error: Timeout waiting for text input selector: {TEXT_INPUT_SELECTOR}. The element was not found or visible within the time limit.")
        raise # Re-raise the exception after printing the specific error
    except Exception as e:
        # Handle any other unexpected errors during the process
        print(f"An unexpected error occurred while entering text: {e}")
        raise # Re-raise the exception


# --- Separate Function to Click Adam Voice ---
def click_adam(page: Page):
    """
    Waits for the Adam voice element and clicks it.

    Args:
        page: The Playwright Page object representing the current browser tab.
    """
    print("Attempting to find and click the 'Adam' voice option...")
    try:
        # Wait until the Adam voice element is visible and enabled
        page.wait_for_selector(ADAM_VOICE_SELECTOR, state='visible', timeout=30000) # Wait up to 30 seconds
        print(f"'Adam' voice element found using selector: {ADAM_VOICE_SELECTOR}")

        # Click the Adam voice element
        page.click(ADAM_VOICE_SELECTOR)
        print("Clicked the 'Adam' voice option.")

    except PlaywrightTimeoutError:
        # Handle timeout specifically if the element doesn't appear
        print(f"Error: Timeout waiting for 'Adam' voice selector: {ADAM_VOICE_SELECTOR}. The element was not found or visible within the time limit.")
        raise # Re-raise the exception after printing the specific error
    except Exception as e:
        # Handle any other unexpected errors during the process
        print(f"An unexpected error occurred while clicking 'Adam' voice: {e}")
        raise # Re-raise the exception


# --- Separate Function to Click Generate Button ---
def click_generate(page: Page):
    """
    Waits for the Generate button element and clicks it.

    Args:
        page: The Playwright Page object representing the current browser tab.
    """
    print("Attempting to find and click the 'Generate' button...")
    try:
        # Wait until the Generate button is visible and enabled
        page.wait_for_selector(GENERATE_BUTTON_SELECTOR, state='visible', timeout=30000) # Wait up to 30 seconds
        print(f"'Generate' button element found using selector: {GENERATE_BUTTON_SELECTOR}")

        # Click the Generate button
        page.click(GENERATE_BUTTON_SELECTOR)
        print("Clicked the 'Generate' button.")

    except PlaywrightTimeoutError:
        # Handle timeout specifically if the element doesn't appear
        print(f"Error: Timeout waiting for 'Generate' button selector: {GENERATE_BUTTON_SELECTOR}. The element was not found or visible within the time limit.")
        raise # Re-raise the exception after printing the specific error
    except Exception as e:
        # Handle any other unexpected errors during the process
        print(f"An unexpected error occurred while clicking 'Generate' button: {e}")
        raise # Re-raise the exception


# --- Separate Function to Click Download Button and Handle Download ---
def click_download(page: Page,filexnamex):
    """
    Waits for the Download button element, clicks it, handles the file download,
    clicks the 'Audio only' option in the dropdown, and waits for 5 seconds.
    Crucially, saves the downloaded file to a permanent location.

    Args:
        page: The Playwright Page object representing the current browser tab.

    Returns:
        The path to the *permanently saved* downloaded file, or None if download fails.
    """
    print("Attempting to find and click the 'Download' button and handle download...")
    downloaded_file_path = None
    try:
        # Wait until the Download button is visible and enabled
        page.wait_for_selector(DOWNLOAD_BUTTON_SELECTOR, state='visible', timeout=60000) # Increased timeout for generation time
        print(f"'Download' button element found using selector: {DOWNLOAD_BUTTON_SELECTOR}")

        # Playwright's download handling
        # Start waiting for the download before clicking the element that triggers it
        with page.expect_download() as download_info:
            page.click(DOWNLOAD_BUTTON_SELECTOR)
            print("Clicked the main 'Download' button.")

            # --- Wait for and click the 'Audio only' option in the dropdown ---
            print("Attempting to find and click the 'Audio only' option in the dropdown...")
            try:
                # Wait for the dropdown container to be visible first
                page.wait_for_selector(DOWNLOAD_DROPDOWN_INNER_SELECTOR, state='visible', timeout=10000)
                print("Download dropdown container is visible.")

                # Wait for the 'Audio only' menu item to be visible and clickable within the dropdown
                audio_only_element = page.wait_for_selector(AUDIO_ONLY_MENU_ITEM_SELECTOR, state='visible', timeout=10000)
                print(f"'Audio only' menu item found using selector: {AUDIO_ONLY_MENU_ITEM_SELECTOR}")

                # Click the 'Audio only' menu item
                audio_only_element.click()
                print("Clicked the 'Audio only' option.")

                # --- Wait for 5 seconds after clicking 'Audio only' ---
                print("Waiting for 5 seconds after clicking 'Audio only'...")
                time.sleep(5) # This wait might still be needed for the download to fully initiate
                print("Wait complete.")
                # --- End Wait ---


            except PlaywrightTimeoutError:
                print(f"Error: Timeout waiting for the download dropdown or 'Audio only' option. Selectors: {DOWNLOAD_DROPDOWN_INNER_SELECTOR}, {AUDIO_ONLY_MENU_ITEM_SELECTOR}. The elements might not have appeared within the time limit.")
                raise # Re-raise the exception
            except Exception as e:
                print(f"An unexpected error occurred while clicking the dropdown menu inner element: {e}")
                raise # Re-raise the exception


        # Get the download object
        download = download_info.value
        print(f"Download started: {download.url}")

        # --- Crucial Step: Save the downloaded file permanently ---
        # Determine the permanent path using the suggested filename
        permanent_file_path = os.path.join(DOWNLOAD_DIRECTORY, filexnamex)
        print(f"Saving downloaded file to: {permanent_file_path}")
        download.save_as(permanent_file_path)
        print("File saved permanently.")
        # --- End Save Step ---

        # The path method here still refers to the temporary path, but save_as ensures it's copied
        # We'll return the permanent path instead
        downloaded_file_path = permanent_file_path
        # print(f"Temporary download path (will be cleaned up): {download.path()}") # Optional: for debugging temporary path


        return downloaded_file_path

    except PlaywrightTimeoutError:
        # Handle timeout specifically if the initial Download button doesn't appear
        print(f"Error: Timeout waiting for initial 'Download' button selector: {DOWNLOAD_BUTTON_SELECTOR}. The element was not found or visible within the time limit.")
        raise # Re-raise the exception after printing the specific error
    except Exception as e:
        # Handle any other unexpected errors during the process
        print(f"An unexpected error occurred during the download process: {e}")
        raise # Re-raise the exception

# --- Separate Function to Check for Login and Perform Login ---
def login_check(page: Page, email: str, password: str):
    """
    Checks if the login page is visible and performs login if necessary.

    Args:
        page: The Playwright Page object.
        email: The user's email address for login.
        password: The user's password for login.

    Returns:
        True if login was performed, False otherwise.
    """
    print(f"Checking for login page (looking for text: '{LOGIN_WELCOME_TEXT}')...")
    try:
        # Check if the welcome text is visible within a short timeout
        page.wait_for_selector(f"text={LOGIN_WELCOME_TEXT}", state='visible', timeout=5000)
        print("Login page detected. Proceeding with login steps.")

        # --- Perform Login Steps ---
        print(f"Attempting to enter email into: {EMAIL_INPUT_SELECTOR}")
        # Use fill() for standard input elements
        page.fill(EMAIL_INPUT_SELECTOR, email)
        print(f"Entered email: {email}")

        print("Clicking Continue button...")
        page.click(CONTINUE_BUTTON_SELECTOR)

        # --- Wait for 5 seconds after clicking Continue ---
        print("Waiting for 5 seconds after clicking Continue...")
        time.sleep(2)
    
        # --- End Wait ---

        # Wait briefly for the password field to appear after clicking continue
        page.fill(PASSWORD_INPUT_SELECTOR, password)

        print(f"Attempting to enter password into: {PASSWORD_INPUT_SELECTOR}")
        # Use click and type for potential non-standard input elements (like the password div)
        page.click(PASSWORD_INPUT_SELECTOR)
        print("Entered password.") # Avoid printing password value

        print("Clicking Sign In button...")
        page.click(SIGN_IN_BUTTON_SELECTOR)

        # Wait for navigation or a key element on the logged-in page to appear
        # You might need to adjust this wait based on what appears after successful login
        print("Waiting for post-login page elements...")
        page.wait_for_load_state('networkidle') # Wait until network is idle
        # Or wait for a specific element that appears after login:
        # page.wait_for_selector("YOUR_POST_LOGIN_ELEMENT_SELECTOR", state='visible', timeout=30000)

        print("Login steps completed.")
        return True # Indicate that login was performed

    except PlaywrightTimeoutError:
        # If the welcome text is not found within the timeout, assume already logged in
        print("Login page text not found. Assuming already logged in or on a different page.")
        return False # Indicate that login was not performed
    except Exception as e:
        print(f"An error occurred during login: {e}")
        raise # Re-raise the exception if login fails


# --- Playwright Automation Workflow Function ---
# This function encapsulates the overall automation steps
def run_capcut_tts_automation(text_to_generate,file_namex):
    file_name = file_namex + ".mp3"
    permanent_save_path = os.path.join(DOWNLOAD_DIRECTORY, file_name)
    
    print(f"Constructed permanent save path: {permanent_save_path}")

    playwright_downloads_dir = os.path.dirname(permanent_save_path)
    if not os.path.exists(playwright_downloads_dir):
        os.makedirs(playwright_downloads_dir)
        print(f"Created Playwright temporary download directory: {playwright_downloads_dir}")

        
    # Use sync_playwright to run synchronously
    with sync_playwright() as p:
        print(f"Using persistent context path: {PERSISTENT_CONTEXT_PATH}")

        # Determine if running headless based on configuration
        # Set to True to run headless after initial manual login
        run_headless = True

        # Launch browser with a persistent context to save login session
        browser = p.chromium.launch_persistent_context(
            PERSISTENT_CONTEXT_PATH,
            headless=run_headless, # Use the variable here
            # Configure download directory for the context
            accept_downloads=True,
            #downloads_path=DOWNLOAD_DIRECTORY, # This is the temporary path Playwright uses first
            downloads_path=playwright_downloads_dir, # Use the directory of the final save path

            # Optional: Set window size (useful in headless) - Can sometimes help with layout issues
            # viewport={'width': 1920, 'height': 1080}
        )

        # Get the first page in the context (or create a new one if needed)
        page = browser.pages[0] if browser.pages else browser.new_page()

        downloaded_file_path = None # Variable to store the downloaded file path

        try:
            # --- Step 1: Navigate directly to Text-to-Speech Tool Page ---
            print(f"Navigating directly to Text-to-Speech tool at {TTS_TOOL_URL}")
            page.goto(TTS_TOOL_URL)

            # --- Step 2: Check for Login and Perform Login if needed ---
            # Pass email and password to the login check function
            login_performed = login_check(page, email, password)

            # --- Wait after potential login/page load for any modals to clear ---
            # This is crucial for headless mode where modals might block interaction.
            # We'll wait for the main text input element to be visible.
            print("Waiting after navigation/login check for main content to be visible...")
            try:
                page.wait_for_selector(TEXT_INPUT_SELECTOR, state='visible', timeout=30000) # Wait up to 30 seconds for visibility
                print("Main text input element is visible. Page should be ready.")
            except PlaywrightTimeoutError:
                 print(f"Timeout waiting for main text input element ({TEXT_INPUT_SELECTOR}) to become visible after navigation/login check.")
                 print("A modal or overlay might still be blocking the page.")
                 raise # Re-raise the exception


            # Manual login prompt - useful if automatic login fails or for initial setup
            # Only prompt if not running headless AND automatic login wasn't performed
            if not run_headless and not login_performed:
                 input("Manual check: Ensure browser is logged in and no modals are blocking. Press Enter to continue...")


            # --- Step 3: Enter Text using the new function ---
            # The wait for text input in capcutEnterText is still needed, but the wait above
            # should reduce the chance of it being blocked.
            capcutEnterText(page, text_to_generate)

            # --- Step 4: Click the 'Adam' voice option ---
            click_adam(page)

            # --- Step 5: Click the 'Generate' button ---
            click_generate(page)

            # --- Step 6: Wait for generation to complete ---
            # Note: A fixed time.sleep is not ideal. Consider waiting for a specific
            # element to appear or disappear indicating generation is complete.
            print("Waiting for generation to potentially complete (10 seconds)...")
            time.sleep(10)
            print("Wait complete.")
            # --- End Wait ---

            # --- Step 7: Click the 'Download' button, handle download, and click 'Audio only' ---
            # This function now saves the file permanently
            downloaded_file_path = click_download(page,file_name)

            print("Automation sequence completed.")

            return {"status": "success", "message": f"TTS generated and downloaded.", "download_path": downloaded_file_path}

        except Exception as e:
            print(f"An error occurred during the script execution: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            # --- Clean up ---
            print("Closing browser context...")
            browser.close()
            print("Script finished.")

# --- Run the automation function ---
if __name__ == '__main__':
    # This block runs when the script is executed directly
    # It calls the main automation function with text, email, and password
    #result = run_capcut_tts_automation(TEXT_TO_GENERATE, CAPCUT_EMAIL, CAPCUT_PASSWORD)
    #print("\nAutomation Result:")
    print("running automation")
