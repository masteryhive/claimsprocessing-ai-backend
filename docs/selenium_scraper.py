from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time

class PriceFinderDataExtractor:
    def __init__(self, email,password):
        self.email = email
        self.password = password

        # Set up Chrome options for headless mode
        chrome_options = Options()
        # Uncomment the below options to run in headless mode
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.url = "https://www.jiji.ng/login.html"
    def extract_data(self):
        # Navigate to the website
        self.driver.get(self.url)
        
        # Wait for the page to load completely
        time.sleep(3)
        
        try:
            # Use XPath to locate the button by its text
            email_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'E-mail or phone')]"))
            )
            email_button.click()
            
            # Wait for navigation or pop-up to load
            time.sleep(2)
            print("Clicked the 'E-mail or phone' button successfully.")
        
        except Exception as e:
            print(f"Error while clicking 'E-mail or phone' button: {e}")

    def close_driver(self):
        # Close the WebDriver
        self.driver.quit()


if __name__ == "__main__":
    # Instantiate the class
    extractor = PriceFinderDataExtractor("sam@masteryhive.ai","hjdbjhbdjhsd")
    try:
        # Call the method to perform the extraction and interaction
        extractor.extract_data()
    finally:
        # Ensure the driver is closed after execution
        extractor.close_driver()
