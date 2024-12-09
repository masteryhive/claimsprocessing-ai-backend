from typing import List
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np
from bs4 import BeautifulSoup
from src.error_trace.errorlogger import log_error

email = "sam@masteryhive.ai"
password = "JLg8m4aQ8n46nhC"


class CostBenchmarking:
    def __init__(self, email=email, password=password):
        self.email = email
        self.password = password

        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--no-sandbox")  # Optional for some environments
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("window-size=1920,1080")
        # chrome_options.add_argument(
        #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.109 Safari/537.36"
        # )
        self.driver = webdriver.Chrome(options=chrome_options)
        self.url = "https://www.jiji.ng/login.html"

    def extract_data(self, search_term: str):
        # Navigate to the website
        self.driver.get(self.url)

        try:
            # Wait for the modal container
            modal_container = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "fw-popup__container"))
            )
            
            # Use JavaScript to scroll the element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", modal_container)
            
            # Find the "E-mail or phone" button within the modal
            email_phone_button = modal_container.find_element(
                By.XPATH, ".//button[contains(span, 'E-mail or phone')]"
            )

            # Ensure the button is visible and interactable
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, ".//button[contains(span, 'E-mail or phone')]"))
            )

            # Click the button
            email_phone_button.click()

            # Wait for the email input field
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "qa-login-field"))
            )

            # Find the password input field
            password_input = self.driver.find_element(
                By.CLASS_NAME, "qa-password-field"
            )

            # Find the login submit button
            login_button = self.driver.find_element(By.CLASS_NAME, "qa-login-submit")

            # Enter email and password
            email_input.send_keys(self.email)
            password_input.send_keys(self.password)

            # Wait for the button to become enabled
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "qa-login-submit"))
            )

            # Click login button
            login_button.click()

            time.sleep(2)
            # # Wait for multiselect input to be present
            # multiselect_input = WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "multiselect__input"))
            # )

            # # Clear any existing text and type the search query
            # multiselect_input.clear()
            # multiselect_input.send_keys("toyota corolla bumper")

            time.sleep(2)

            # # Send ENTER key to select first suggestion or submit search
            # multiselect_input.send_keys(Keys.ENTER)
            search_term = search_term.replace(" ", "%20")
            # Direct navigation to the filtered search URL
            search_url = f"https://jiji.ng/lagos/search?query={search_term}&filter_id_verify=Verified%20sellers&sort=new"
            self.driver.get(search_url)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "qa-advert-price"))
            )
            # Get the page content and parse it with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            price_elements = soup.find_all("div", {"class": "qa-advert-price"})

            # Limit to first 20 elements
            price_elements = price_elements[:50]

            # Extract and clean prices
            prices = []
            for element in price_elements:
                # Get text and remove special characters
                price_text = element.text
                # Remove currency symbols, commas, spaces
                cleaned_price_text = "".join(
                    char for char in price_text if char.isdigit()
                )

                # Convert to integer
                try:
                    price = int(cleaned_price_text)
                    prices.append(price)
                except ValueError:
                    print(f"Could not convert price: {price_text}")
            time.sleep(2)
            return prices
        except Exception as e:
            print(f"Error locating or clicking 'E-mail or phone' button: {e}")

    def close_driver(self):
        # Close the WebDriver
        self.driver.quit()

    def remove_outliers(
        self, prices: List[float], threshold: float = 1.5
    ) -> List[float]:
        """
        Removes outliers from the price list using the IQR method.

        Parameters:
        prices (List[float]): List of prices
        threshold (float): Number of IQR ranges to consider for outlier detection

        Returns:
        List[float]: Prices with outliers removed
        """
        prices_array = np.array(prices)
        q1 = np.percentile(prices_array, 25)
        q3 = np.percentile(prices_array, 75)
        iqr = q3 - q1

        lower_bound = q1 - (threshold * iqr)
        upper_bound = q3 + (threshold * iqr)

        return [x for x in prices if lower_bound <= x <= upper_bound]

    def analyze_price_realism(
        self, market_prices: List[float], quoted_price: float, threshold: float = 1.5
    ) -> dict:
        """
        Analyzes if a quoted price is realistic based on market data using statistical methods.

        Parameters:
        market_prices (List[float]): List of known market prices
        quoted_price (float): The price to analyze
        threshold (float): Number of IQR ranges to consider for outlier detection (default 1.5)

        Returns:
        dict: Analysis results including whether the price is realistic and supporting statistics
        """
        # Convert to numpy array for statistical calculations
        prices = np.array(market_prices)

        # Calculate basic statistics
        median_price = np.median(prices)
        q1 = np.percentile(prices, 25)
        q3 = np.percentile(prices, 75)
        iqr = q3 - q1

        # Define bounds for realistic prices
        lower_bound = q1 - (threshold * iqr)
        upper_bound = q3 + (threshold * iqr)

        # Calculate percentage difference from median
        percent_diff_from_median = ((quoted_price - median_price) / median_price) * 100

        # Determine if price is realistic
        is_realistic = lower_bound <= quoted_price <= upper_bound

        # Calculate what percentile the quoted price falls into
        percentile = np.percentile(prices, [0, 25, 50, 75, 100])
        price_percentile = (
            sum(1 for x in prices if x < quoted_price) / len(prices) * 100
        )

        return {
            "is_realistic": is_realistic,
            "analysis": {
                "median_price": median_price,
                "price_range": {"lower_bound": lower_bound, "upper_bound": upper_bound},
                "market_statistics": {
                    "minimum": np.min(prices),
                    "maximum": np.max(prices),
                    "q1": q1,
                    "q3": q3,
                },
                "quoted_price_percentile": price_percentile,
                "percent_difference_from_median": percent_diff_from_median,
            },
        }

    def analyze_price(self, market_prices: List[float], quoted_price: float) -> None:
        """
        Helper function to print a human-readable analysis of the price.
        """
        # First remove outliers
        cleaned_prices = self.remove_outliers(market_prices)

        # print(f"\nOriginal number of prices: {len(market_prices)}")
        # print(f"Number of prices after removing outliers: {len(cleaned_prices)}")

        result = self.analyze_price_realism(cleaned_prices, quoted_price)

        print(f"\nAnalysis for quoted price: {quoted_price:,.0f}")
        print("-" * 50)
        status = ""
        if result["is_realistic"]:
            print("✅ This price appears REALISTIC based on market data")
            status = "✅ This price appears REALISTIC based on market data"
        else:
            print("❌ This price appears UNREALISTIC based on market data")
            status = "❌ This price appears UNREALISTIC based on market data"

        analysis = result["analysis"]
        # print(f"\nMarket Statistics (after removing outliers):")
        # print(f"- Median price: {analysis['median_price']:,.0f}")
        # print(
        #     f"- Realistic price range: {analysis['price_range']['lower_bound']:,.0f} to {analysis['price_range']['upper_bound']:,.0f}"
        # )
        # print(
        #     f"- Your price is in the {analysis['quoted_price_percentile']:.1f}th percentile"
        # )
        # print(f"- Difference from median: {analysis['percent_difference_from_median']:+.1f}%")
        market_statistics = {
            "median_price": analysis['median_price'],
            "realistic_price_range": f"{analysis['price_range']['lower_bound']:,.0f} to {analysis['price_range']['upper_bound']:,.0f}",
            "quoted_price_percentile": f"- Your price is in the {analysis['quoted_price_percentile']:.1f}th percentile",
            "status":status
        }
        return market_statistics
    
    def run(self, search_term: str, quoted_price: str):
        try:
            market_prices = self.extract_data(search_term)
            quoted_price = float(quoted_price.replace(",", ""))
            return self.analyze_price(market_prices, quoted_price)
        except Exception as e:
            log_error(e)
        finally:
            self.close_driver()

    def get_expected_price_range(
        self, prices: List[float], threshold: float = 1.5
    ) -> str:
        """
        Calculates the expected price range based on the list of prices.

        Parameters:
        prices (List[float]): List of market prices.
        threshold (float): Number of IQR ranges to consider for defining the range.

        Returns:
        str: The expected price range in a formatted string.
        """
        # Remove outliers to clean the data
        cleaned_prices = self.remove_outliers(prices, threshold)

        if not cleaned_prices:
            return "Not enough valid data to determine the price range."

        # Convert to numpy array for statistical calculations
        prices_array = np.array(cleaned_prices)

        # Calculate Q1 and Q3
        q1 = np.percentile(prices_array, 25)
        q3 = np.percentile(prices_array, 75)

        # Return the expected price range as a formatted string
        return f"{int(q1):,} - {int(q3):,}"

    def run_with_expected_range(self, search_term: str):
        """
        Extends the `run` method to include the expected price range in the output.

        Parameters:
        search_term (str): The search term to query.
        quoted_price (str): The quoted price to analyze.

        Returns:
        dict: The analysis results and the expected price range.
        """
        try:
            market_prices = self.extract_data(search_term)
            expected_range = self.get_expected_price_range(market_prices)
            return f"Expected price range for '{search_term}': {expected_range}"
        except Exception as e:
            log_error(e)
        finally:
            self.close_driver()
