from seleniumbase import Driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import json
import csv
import pandas as pd
import undetected_chromedriver as uc
import requests
from fake_useragent import UserAgent
from random import uniform, choice
import platform

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HumanBehavior:
    """Class to handle human-like behavior"""
    
    COMMON_USERAGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edge/120.0.0.0"
    ]

    @staticmethod
    def get_random_useragent():
        """Get a random user agent"""
        try:
            ua = UserAgent()
            return ua.chrome
        except:
            return choice(HumanBehavior.COMMON_USERAGENTS)

    @staticmethod
    def add_human_behavior(driver):
        """Add various human-like behaviors to the browser"""
        try:
            # Random scroll
            driver.execute_script("""
                window.scrollTo({
                    top: Math.floor(Math.random() * 100),
                    behavior: 'smooth'
                });
            """)
            time.sleep(uniform(0.5, 1.5))
            
            # Random mouse movements (simulated via JavaScript)
            driver.execute_script("""
                const e = document.createEvent('MouseEvents');
                e.initMouseEvent(
                    'mousemove',
                    true,
                    true,
                    window,
                    0,
                    Math.floor(Math.random() * window.innerWidth),
                    Math.floor(Math.random() * window.innerHeight),
                    Math.floor(Math.random() * window.innerWidth),
                    Math.floor(Math.random() * window.innerHeight)
                );
                document.dispatchEvent(e);
            """)
            
        except Exception as e:
            logger.warning(f"Failed to add human behavior: {str(e)}")

    @staticmethod
    def get_system_specific_options():
        """Get system-specific Chrome options"""
        options = uc.ChromeOptions()
        system = platform.system().lower()
        
        if system == "windows":
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
        elif system == "linux":
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
        
        return options

def solve_with_2captcha(sitekey, url, api_key):
    """Solve Turnstile using 2captcha"""
    try:
        # Create task
        create_task_url = "https://api.2captcha.com/createTask"
        task_payload = {
            "clientKey": api_key,
            "task": {
                "type": "TurnstileTaskProxyless",
                "websiteURL": url,
                "websiteKey": sitekey
            }
        }
        
        logger.info("Creating 2captcha task")
        response = requests.post(create_task_url, json=task_payload)
        task_id = response.json().get('taskId')
        
        if not task_id:
            logger.error("Failed to create 2captcha task")
            return None
            
        # Get result
        get_result_url = "https://api.2captcha.com/getTaskResult"
        result_payload = {
            "clientKey": api_key,
            "taskId": task_id
        }
        
        # Poll for result
        max_attempts = 30
        attempt = 0
        while attempt < max_attempts:
            logger.info(f"Checking 2captcha result (attempt {attempt + 1})")
            response = requests.post(get_result_url, json=result_payload)
            result = response.json()
            
            if result.get('status') == 'ready':
                token = result.get('solution', {}).get('token')
                if token:
                    logger.info("Successfully got token from 2captcha")
                    return token
                    
            time.sleep(5)
            attempt += 1
            
        logger.error("Timed out waiting for 2captcha result")
        return None
        
    except Exception as e:
        logger.error(f"Error in 2captcha solve: {str(e)}")
        return None

def click_discover(driver):
    """Click the Discover element if it exists"""
    try:
        discover_element = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Discover']"))
        )
        logger.info("Found Discover element, attempting to click")
        # Using JavaScript click
        driver.execute_script("arguments[0].click();", discover_element)
        logger.info("Successfully clicked Discover")
        return True
    except Exception as e:
        logger.error(f"Failed to click Discover: {str(e)}")
        return False

def extract_titles(driver, num_titles=10):
    """Extract titles from the discover page"""
    try:
        # Wait for titles to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="thread-title"]'))
        )
        
        # Get all title elements
        titles = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="thread-title"]')
        
        # Extract text from first num_titles elements
        title_texts = [title.text for title in titles[:num_titles]]
        logger.info(f"Successfully extracted {len(title_texts)} titles")
        
        # Save to CSV
        df = pd.DataFrame(title_texts, columns=['Title'])
        df.to_csv('perplexity_titles.csv', index=False)
        logger.info("Saved titles to perplexity_titles.csv")
        
        return title_texts
    except Exception as e:
        logger.error(f"Failed to extract titles: {str(e)}")
        return []

# Custom script to intercept Turnstile parameters
custom_js = """
// Store captured data
window.capturedData = {};

// Intercept Turnstile parameters
const i = setInterval(() => {
    if (window.turnstile) {
        clearInterval(i);
        console.log('Found turnstile object, intercepting render method');
        const originalRender = window.turnstile.render;
        window.turnstile.render = function(container, params) {
            console.log('Turnstile render called with:', params);
            window.capturedData.turnstile = {
                type: "TurnstileTaskProxyless",
                websiteKey: params.sitekey,
                websiteURL: window.location.href,
                data: params.cData,
                pagedata: params.chlPageData,
                action: params.action,
                userAgent: navigator.userAgent
            };
            window.tsCallback = params.callback;
            console.log('Captured data:', JSON.stringify(window.capturedData.turnstile));
            return originalRender.apply(this, arguments);
        };
        console.log('Turnstile interceptor initialized');
    }
}, 10);

console.log('Interceptor initialized');
"""

try:
    # Initialize the driver with human-like behavior
    logger.info("Initializing driver")
    chrome_options = HumanBehavior.get_system_specific_options()
    chrome_options.add_argument(f'user-agent={HumanBehavior.get_random_useragent()}')
    chrome_options.add_argument('--window-size=1920,1080')
    driver = Driver(uc=True, browser='chrome', headed=False)

    # Navigate to perplexity.ai with human-like behavior
    logger.info("Navigating to perplexity.ai")
    driver.uc_open_with_reconnect("https://www.perplexity.ai", 4)
    HumanBehavior.add_human_behavior(driver)

    # Before clicking captcha
    HumanBehavior.add_human_behavior(driver)
    # Try GUI click first
    logger.info("Attempting GUI click on captcha")
    try:
        driver.uc_gui_click_captcha()
        logger.info("GUI click successful")
        gui_click_successful = True
    except Exception as e:
        logger.warning(f"GUI click failed: {str(e)}")
        gui_click_successful = False

    # If GUI click failed, try 2captcha
    if not gui_click_successful:
        logger.info("Attempting 2captcha solve")
        # Get sitekey from the page
        sitekey = driver.execute_script("""
            return document.querySelector('iframe[src*="challenges.cloudflare.com"]')
                   ?.getAttribute('data-sitekey') || '';
        """)
        
        if sitekey:
            # Replace with your 2captcha API key
            api_key = "YOUR_2CAPTCHA_API_KEY"
            token = solve_with_2captcha(sitekey, "https://www.perplexity.ai", api_key)
            
            if token:
                # Submit the token
                driver.execute_script(f"""
                    window.turnstile?.callback?.('{token}');
                """)
                logger.info("Submitted 2captcha token")

    # Wait a moment for potential auto-solve
    time.sleep(2)

    # Check if captcha was solved by looking for "Discover" text
    try:
        discover_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Discover']"))
        )
        logger.info("Captcha was solved automatically by uc_gui_click_captcha!")
        is_solved = True
    except:
        logger.info("'Discover' element not found, captcha might not be solved")
        is_solved = False
    
    if not is_solved:
        logger.info("Captcha not solved automatically, attempting to intercept parameters")
        # Inject our interceptor script
        logger.info("Injecting interceptor script")
        driver.execute_script(custom_js)

        # Wait for Turnstile parameters to be captured
        logger.info("Waiting for Turnstile parameters to be captured")
        max_attempts = 10
        attempt = 0
        captured_data = None
        
        while attempt < max_attempts:
            try:
                captured_data = driver.execute_script("return window.capturedData?.turnstile;")
                if captured_data:
                    break
                    
                # Add debug information
                debug_info = driver.execute_script("""
                    return {
                        documentState: document.readyState,
                        url: window.location.href,
                        turnstileExists: !!window.turnstile,
                        turnstileRenderModified: window.turnstile && window.turnstile.render.toString().includes('capturedData'),
                        capturedData: window.capturedData
                    }
                """)
                logger.info(f"Debug info - Attempt {attempt}: {json.dumps(debug_info)}")
                
            except Exception as e:
                logger.warning(f"Error during attempt {attempt}: {str(e)}")
                
            time.sleep(1)
            attempt += 1

        if captured_data:
            logger.info(f"Successfully captured Turnstile parameters: {json.dumps(captured_data, indent=2)}")
            # Save the captured data to a file
            with open('turnstile_params.json', 'w') as f:
                json.dump(captured_data, f, indent=2)
            logger.info("Saved parameters to turnstile_params.json")
        else:
            logger.error("Failed to capture Turnstile parameters after maximum attempts")
            raise Exception("Failed to capture Turnstile parameters")

    # Try to click Discover after captcha is solved
    if is_solved:
        HumanBehavior.add_human_behavior(driver)
        if click_discover(driver):
            # Add random delay before extraction
            time.sleep(uniform(2, 4))
            # Extract titles
            titles = extract_titles(driver)
            if titles:
                logger.info("Extracted titles:")
                for i, title in enumerate(titles, 1):
                    logger.info(f"{i}. {title}")

except Exception as e:
    logger.error(f"An error occurred: {str(e)}", exc_info=True)

finally:
    logger.info("Closing browser")
    try:
        driver.quit()
    except:
        pass
