from typing import Annotated, List
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np
from bs4 import BeautifulSoup
from typing import List
from src.error_trace.errorlogger import log_error
from playwright.sync_api import sync_playwright, Page
class CostBenchmarking:
    def __init__(self, email:str, password:str):
        self.email = email
        self.password = password

     
    def create_driver(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--no-sandbox")  # Optional for some environments
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--start-maximized")
        # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--disable-infobars")
        # chrome_options.add_argument("window-size=1920,1080")
        # chrome_options.add_argument(
        #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.109 Safari/537.36"
        # )
        return webdriver.Chrome(options=chrome_options)

    def fetch_market_data(self, search_term: str):
        driver = None

        try:
            # Navigate to the website
            driver = self.create_driver()
            driver.get("https://www.jiji.ng/login.html")
            # Wait for the modal container
            modal_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "fw-popup__container"))
            )
            
            # Use JavaScript to scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", modal_container)
            
            time.sleep(2)

            # Ensure the button is visible and interactable
            email_phone_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "fw-button.qa-fw-button.fw-button--type-success.fw-button--size-large.h-width-100p.h-bold")))

            # Click the button
            email_phone_button.click()

            # Wait for the email input field
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "qa-login-field"))
            )

            # Find the password input field
            password_input = driver.find_element(
                By.CLASS_NAME, "qa-password-field"
            )

            # Enter email and password
            email_input.send_keys(self.email)
            password_input.send_keys(self.password)

            # Find the login submit button
            login_button = driver.find_element(By.CLASS_NAME, "qa-login-submit")

 
            # Wait for the button to become enabled
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "qa-login-submit"))
            )

            # Click login button
            login_button.click()

            time.sleep(5)

            # # Send ENTER key to select first suggestion or submit search
            # multiselect_input.send_keys(Keys.ENTER)
            search_term = search_term.replace(" ", "%20")
            # Direct navigation to the filtered search URL
            search_url = f"https://jiji.ng/lagos/search?query={search_term}&filter_id_verify=Verified%20sellers&sort=new"
            driver.get(search_url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "qa-advert-price"))
            )
            # Get the page content and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, "html.parser")

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
            time.sleep(5)
            return prices

        except TimeoutException as e:
            print(f"Error: {e}")
            return []  # Return empty list on error
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass  # Ignore errors during quit

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
    def new_analyze_price_realism(self,prices, quote_price):
        """
        Analyze if the quoted price is realistic compared to a list of trader prices.

        Args:
            prices (list or np.ndarray): A list of prices from traders.
            quote_price (float): The quoted price to analyze.

        Returns:
            dict: A dictionary containing analysis results.

        Interpretation of Results:
            - mean_price: The average price from the traders. A quoted price close to this value aligns with the central tendency.
            - median_price: The middle value of the dataset. A quoted price near the median indicates alignment with typical trader prices.
            - std_dev: The spread of the prices. A lower standard deviation indicates less variability in the data.
            - z_score: Indicates how many standard deviations the quoted price is from the mean. Values close to 0 mean the quoted price is typical.
            - percentile: The percentile rank of the quoted price. A value near 50% indicates the quoted price is in the middle of the distribution.
            - is_outlier: A boolean indicating whether the quoted price is an outlier. False means the price is within the expected range.
            - lower_bound and upper_bound: Define the range where most trader prices fall. A quoted price within this range is realistic.
        """
        # Ensure prices are in a numpy array
        prices = np.array(prices)

        # Calculate statistics
        mean_price = np.mean(prices)
        median_price = np.median(prices)
        std_dev = np.std(prices)

        # Z-score calculation
        z_score = (quote_price - mean_price) / std_dev

        # Percentile calculation
        percentile = np.sum(prices <= quote_price) / len(prices) * 100

        # IQR calculation for outlier detection
        q1 = np.percentile(prices, 25)
        q3 = np.percentile(prices, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Outlier check
        is_outlier = quote_price < lower_bound or quote_price > upper_bound
        z_score_close_to_zero = abs(z_score) < 0.1
        # Return analysis results
        analysis_result = {
            "analysis": {
            "mean_price": mean_price,
            "median_price": median_price,
            "std_dev": std_dev,
            "z_score": z_score,
            "quoted_price_percentile": percentile,
            "is_outlier": is_outlier,
            "price_range": {"lower_bound": lower_bound, "upper_bound": upper_bound},
        }
        }
        if z_score_close_to_zero:
            analysis_result["is_realistic"]= True
        else:
            analysis_result["is_realistic"]= False

        return analysis_result
    
    def analyze_price(self, market_prices: List[float], quoted_price: float) -> None:
        """
        Helper function to print a human-readable analysis of the price.
        """
        # First remove outliers
        cleaned_prices = self.remove_outliers(market_prices)

        # print(f"\nOriginal number of prices: {len(market_prices)}")
        # print(f"Number of prices after removing outliers: {len(cleaned_prices)}")

        result = self.new_analyze_price_realism(cleaned_prices, quoted_price)
        status = ""
        if result["is_realistic"]:
            status = "✅ This price appears REALISTIC based on market data"
        else:
            status = "❌ This price appears UNREALISTIC based on market data"

        analysis = result["analysis"]
        market_statistics = (
            f"\nAnalysis for quoted price: {quoted_price:,.0f}"
            "\n--------------------------------------------------------------\n"
            f"median_price: {analysis['median_price']}\n"
            f"realistic_price_range: {analysis['price_range']['lower_bound']:,.0f} to {analysis['price_range']['upper_bound']:,.0f}\n"
            f"quoted_price_percentile: - Your price is in the {analysis['quoted_price_percentile']:.1f}th percentile\n"
            f"status: {status}"
        )
        return market_statistics
    
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
    

    def item_cost_analysis(self, market_prices: list, quoted_price: str):
        try:
            quoted_price = float(quoted_price.replace(",", ""))
            return self.analyze_price(market_prices, quoted_price)
        except Exception as e:
            log_error(e)

    def run_with_expected_range(self, search_term:str,market_prices: list):
        """
        Extends the `run` method to include the expected price range in the output.

        Parameters:
        search_term (str): The search term to query.
        quoted_price (str): The quoted price to analyze.

        Returns:
        dict: The analysis results and the expected price range.
        """
        try:
            expected_range = self.get_expected_price_range(market_prices)
            return f"Expected price range for '{search_term}': {expected_range}"
        except Exception as e:
            log_error(e)


class CostBenchmarkingPlaywright:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def create_driver(self) -> Page:
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,  # Set to True for production
            args=[
            '--disable-dev-shm-usage',  # Required for Docker
            '--no-sandbox',  # Required for Docker
            '--disable-gpu',  # Optional: Disable GPU hardware acceleration
            '--disable-setuid-sandbox',  # Required for Docker
        ]
        )
        self.context = self.browser.new_context(
            # viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.109 Safari/537.36'
        )
        return self.context.new_page()

    def fetch_market_data(self, search_term: str) -> List[int]:
        try:
            # Create new page
            self.page = self.create_driver()
            
            # Navigate to login page
            self.page.goto("https://www.jiji.ng/login.html")
            
            # Wait for and click the email/phone button
            self.page.wait_for_selector(".fw-button.qa-fw-button.fw-button--type-success.fw-button--size-large.h-width-100p.h-bold")
            self.page.click(".fw-button.qa-fw-button.fw-button--type-success.fw-button--size-large.h-width-100p.h-bold")
            time.sleep(2)
            # Fill login credentials
            self.page.fill(".qa-login-field", self.email)
            self.page.fill(".qa-password-field", self.password)
            time.sleep(2)
            # Click login button and wait for navigation
            self.page.click(".qa-login-submit")
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)
            # Navigate to search results
            search_term = search_term.replace(" ", "%20")
            search_url = f"https://jiji.ng/lagos/search?query={search_term}&filter_id_verify=Verified%20sellers&sort=new"
            self.page.goto(search_url)
            time.sleep(2)
            # Wait for prices to load
            self.page.wait_for_selector(".qa-advert-price")
            
            # Extract prices using BeautifulSoup
            soup = BeautifulSoup(self.page.content(), "html.parser")
            price_elements = soup.find_all("div", {"class": "qa-advert-price"})
            price_elements = price_elements[:50]  # Limit to first 50 elements

            # Extract and clean prices
            prices = []
            for element in price_elements:
                price_text = element.text
                cleaned_price_text = "".join(char for char in price_text if char.isdigit())
                try:
                    price = int(cleaned_price_text)
                    prices.append(price)
                except ValueError:
                    print(f"Could not convert price: {price_text}")

            return prices

        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
        finally:
            self.close_driver()

    def close_driver(self):
        """Clean up Playwright resources"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"Error closing driver: {e}")

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
    
    def new_analyze_price_realism(self,prices, quote_price):
        """
        Analyze if the quoted price is realistic compared to a list of trader prices.

        Args:
            prices (list or np.ndarray): A list of prices from traders.
            quote_price (float): The quoted price to analyze.

        Returns:
            dict: A dictionary containing analysis results.

        Interpretation of Results:
            - mean_price: The average price from the traders. A quoted price close to this value aligns with the central tendency.
            - median_price: The middle value of the dataset. A quoted price near the median indicates alignment with typical trader prices.
            - std_dev: The spread of the prices. A lower standard deviation indicates less variability in the data.
            - z_score: Indicates how many standard deviations the quoted price is from the mean. Values close to 0 mean the quoted price is typical.
            - percentile: The percentile rank of the quoted price. A value near 50% indicates the quoted price is in the middle of the distribution.
            - is_outlier: A boolean indicating whether the quoted price is an outlier. False means the price is within the expected range.
            - lower_bound and upper_bound: Define the range where most trader prices fall. A quoted price within this range is realistic.
        """
        # Ensure prices are in a numpy array
        prices = np.array(prices)

        # Calculate statistics
        mean_price = np.mean(prices)
        median_price = np.median(prices)
        std_dev = np.std(prices)

        # Z-score calculation
        z_score = (quote_price - mean_price) / std_dev

        # Percentile calculation
        percentile = np.sum(prices <= quote_price) / len(prices) * 100

        # IQR calculation for outlier detection
        q1 = np.percentile(prices, 25)
        q3 = np.percentile(prices, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Outlier check
        is_outlier = quote_price < lower_bound or quote_price > upper_bound
        z_score_close_to_zero = abs(z_score) < 0.1
        # Return analysis results
        analysis_result = {
            "analysis": {
            "mean_price": mean_price,
            "median_price": median_price,
            "std_dev": std_dev,
            "z_score": z_score,
            "quoted_price_percentile": percentile,
            "is_outlier": is_outlier,
            "price_range": {"lower_bound": lower_bound, "upper_bound": upper_bound},
        }
        }
        if z_score_close_to_zero:
            analysis_result["is_realistic"]= True
        else:
            analysis_result["is_realistic"]= False

        return analysis_result
    
    def analyze_price(self, market_prices: List[float], quoted_price: float) -> None:
        """
        Helper function to print a human-readable analysis of the price.
        """
        # First remove outliers
        cleaned_prices = self.remove_outliers(market_prices)

        # print(f"\nOriginal number of prices: {len(market_prices)}")
        # print(f"Number of prices after removing outliers: {len(cleaned_prices)}")

        result = self.new_analyze_price_realism(cleaned_prices, quoted_price)
        status = ""
        if result["is_realistic"]:
            status = "✅ This price appears REALISTIC based on market data"
        else:
            status = "❌ This price appears UNREALISTIC based on market data"

        analysis = result["analysis"]
        market_statistics = (
            f"\nAnalysis for quoted price: {quoted_price:,.0f}"
            "\n--------------------------------------------------------------\n"
            f"median_price: {analysis['median_price']}\n"
            f"realistic_price_range: {analysis['price_range']['lower_bound']:,.0f} to {analysis['price_range']['upper_bound']:,.0f}\n"
            f"quoted_price_percentile: - Your price is in the {analysis['quoted_price_percentile']:.1f}th percentile\n"
            f"status: {status}"
        )
        return market_statistics
    
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
    
    def item_cost_analysis(self, market_prices: list, quoted_price: str):
        try:
            quoted_price = float(quoted_price.replace(",", ""))
            return self.analyze_price(market_prices, quoted_price)
        except Exception as e:
            log_error(e)
        finally:
            self.close_driver()

    def run_with_expected_range(self, search_term: str, market_prices: list):
        try:
            expected_range = self.get_expected_price_range(market_prices)
            return f"Expected price range for '{search_term}': {expected_range}"
        except Exception as e:
            log_error(e)
        finally:
            self.close_driver()

# c = CostBenchmarkingPlaywright(email = "sam@masteryhive.ai",
#         password = "JLg8m4aQ8n46nhC")
# print(c.fetch_market_data("hyundai sonata side mirror tokunbo"))