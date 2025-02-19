from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import pytesseract
import time
from datetime import datetime
import os
import platform
import re
import pandas as pd
import logging
from typing import Optional, Tuple

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Use the unquarantined ChromeDriver
    service = Service('/opt/homebrew/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/stock_scraper.log'),
            logging.StreamHandler()
        ]
    )

def extract_price_data(text: str) -> Tuple[Optional[float], Optional[float], Optional[str]]:
    """Extract price, change amount, and change percentage from OCR text."""
    try:
        # Extract the main price (e.g., $138.74)
        price_match = re.search(r'\$([\d,]+\.?\d*)', text)
        price = float(price_match.group(1).replace(',', '')) if price_match else None

        # Extract the change amount (e.g., -0.66)
        change_match = re.search(r'([+-]\d+\.\d+)\s+Today', text)
        change = float(change_match.group(1)) if change_match else None

        # Extract the percentage change (e.g., -0.47%)
        percent_match = re.search(r'([+-]?\d+\.\d+)%', text)
        percent = percent_match.group(0) if percent_match else None

        return price, change, percent
    except Exception as e:
        logging.error(f"Error parsing price data: {e}")
        return None, None, None

def save_to_csv(timestamp: datetime, price: float, change: float, percent: str):
    """Save the stock data to a CSV file."""
    csv_file = 'data/nvidia_stock_prices.csv'
    data = {
        'timestamp': [timestamp],
        'price': [price],
        'change': [change],
        'percent_change': [percent]
    }
    df = pd.DataFrame(data)
    
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        os.makedirs('data', exist_ok=True)
        df.to_csv(csv_file, index=False)

def capture_stock_price() -> bool:
    """Capture and process stock price data. Returns True if successful."""
    driver = None
    try:
        # Create output directory if it doesn't exist
        os.makedirs('screenshots', exist_ok=True)

        driver = setup_driver()
        
        # Navigate to NVIDIA stock page
        url = "https://www.google.com/finance/quote/NVDA:NASDAQ"
        driver.get(url)
        
        # Wait for the price element to be visible
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-last-price]"))
        )
        
        # Get the timestamp
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y%m%d_%H%M%S")
        
        # Take screenshot of the price element
        screenshot_path = f"screenshots/nvidia_stock_{timestamp}.png"
        price_element.screenshot(screenshot_path)
        
        # Use OCR to extract the price
        image = Image.open(screenshot_path)
        price_text = pytesseract.image_to_string(image).strip()
        
        # Extract and validate price data
        price, change, percent = extract_price_data(price_text)
        
        if price is None:
            logging.error(f"Failed to extract valid price from text: {price_text}")
            return False
            
        # Save data to CSV
        save_to_csv(current_time, price, change, percent)
        
        logging.info(f"Price: ${price:.2f} | Change: {change:+.2f} ({percent})")
        return True
        
    except TimeoutException:
        logging.error("Timeout waiting for price element to load")
        return False
    except WebDriverException as e:
        logging.error(f"WebDriver error: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return False
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    setup_logging()
    logging.info("Starting NVIDIA stock price monitoring (5-second intervals)")
    
    # Configuration
    INTERVAL_SECONDS = 5
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    try:
        driver = setup_driver()  # Create a single driver instance
        logging.info("Browser initialized successfully")
        
        while True:
            try:
                # Navigate to NVIDIA stock page
                url = "https://www.google.com/finance/quote/NVDA:NASDAQ"
                driver.get(url)
                
                # Wait for the price element to be visible
                price_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-last-price]"))
                )
                
                # Get the timestamp
                current_time = datetime.now()
                timestamp = current_time.strftime("%Y%m%d_%H%M%S")
                
                # Create temporary screenshot
                temp_screenshot = f"temp_screenshot_{timestamp}.png"
                price_element.screenshot(temp_screenshot)
                
                try:
                    # Use OCR to extract the price
                    image = Image.open(temp_screenshot)
                    price_text = pytesseract.image_to_string(image).strip()
                    
                    # Extract and validate price data
                    price, change, percent = extract_price_data(price_text)
                    
                    if price is not None:
                        # Save data to CSV
                        save_to_csv(current_time, price, change, percent)
                        logging.info(f"Price: ${price:.2f} | Change: {change:+.2f} ({percent})")
                    else:
                        logging.warning(f"Failed to extract valid price from text: {price_text}")
                        
                finally:
                    # Clean up: remove the temporary screenshot
                    try:
                        os.remove(temp_screenshot)
                    except Exception as e:
                        logging.warning(f"Failed to remove temporary screenshot: {e}")
                
            except Exception as e:
                logging.error(f"Error during capture: {e}")
                # Reinitialize the driver if there's an error
                try:
                    driver.quit()
                except:
                    pass
                driver = setup_driver()
            
            # Wait for the next interval
            time.sleep(INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user")
    except Exception as e:
        logging.error(f"Program terminated due to error: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

