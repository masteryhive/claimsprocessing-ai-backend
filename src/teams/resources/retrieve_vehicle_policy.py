import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium import webdriver
from contextlib import contextmanager
from queue import Queue, Empty
from threading import Lock
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

class WebDriverPool:
    def __init__(self, max_drivers: int = 50):
        self.max_drivers = max_drivers
        self.drivers: Queue = Queue()
        self.active_drivers = 0
        self.lock = Lock()
        
    def _create_driver(self) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.109 Safari/537.36"
        )
        return webdriver.Chrome(options=chrome_options)
    
    @contextmanager
    def acquire(self, timeout: Optional[float] = None) -> webdriver.Chrome:
        driver = None
        created = False
        
        try:
            # Try to get an existing driver from the pool
            driver = self.drivers.get(block=False)
        except Empty:
            # If no driver is available, try to create a new one if under max limit
            with self.lock:
                if self.active_drivers < self.max_drivers:
                    driver = self._create_driver()
                    self.active_drivers += 1
                    created = True
                    
        if driver is None:
            # If we couldn't create a new driver, wait for an existing one
            try:
                driver = self.drivers.get(timeout=timeout)
            except Empty:
                raise TimeoutError("No available drivers in the pool")
                
        try:
            yield driver
        finally:
            # Return driver to pool if it's still good, otherwise clean up
            try:
                driver.current_url  # Check if driver is still responsive
                self.drivers.put(driver)
            except:
                if driver:
                    driver.quit()
                with self.lock:
                    self.active_drivers -= 1

    def shutdown(self):
        while not self.drivers.empty():
            driver = self.drivers.get()
            driver.quit()
    


class InsuranceDataExtractor:
    # Class-level driver pool
    driver_pool = WebDriverPool(max_drivers=50)  # Adjust max_drivers based on system resources

    def __init__(self, registration_number:str):
        self.registration_number = registration_number
        self.url = "https://www.askniid.org/VerifyPolicy.aspx"

    def extract_data(self):
        with self.driver_pool.acquire(timeout=30) as driver:  # 30 second timeout for getting a driver
            try:
                return self._perform_extraction(driver)
            except Exception as e:
                print(f"Extraction error: {str(e)}")
                raise

    def _perform_extraction(self, driver):       
        driver.get(self.url)

        dropdown = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_drpOption"))
        )
        dropdown = Select(dropdown)
        dropdown.select_by_value("Single")

        radio_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_rblNumber_1"))
        )
        radio_button.click()

        registration_number_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_txtNumber"))
        )
        registration_number_input.send_keys(self.registration_number)

        # Wait for search button to be clickable
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_btnSearch"))
        )

        search_button.click()

        try:
            # Wait for the policy number element to be present with an extended timeout
            WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_lblPolicyNo"))
                )
        except TimeoutException:
            # Wait for the policy number element to be present with an extended timeout
            WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_Div1"))
                )
            # Extract the data
            soup = BeautifulSoup(driver.page_source, "html.parser")
            policy_state = soup.find("span", {"id": "ContentPlaceHolder1_lblinfo"}).text
            return policy_state
        else:
            # Additional wait to ensure page is fully loaded
            time.sleep(5)

            # Extract the data
            soup = BeautifulSoup(driver.page_source, "html.parser")
            policy_number = soup.find("span", {"id": "ContentPlaceHolder1_lblPolicyNo"}).text
            new_registration_number = soup.find("span", {"id": "ContentPlaceHolder1_lblNewRegistrationNo"}).text
            registration_number = soup.find("span", {"id": "ContentPlaceHolder1_lblRegistrationNo"}).text
            type_of_cover = soup.find("span", {"id": "ContentPlaceHolder1_lblTypeOfCover"}).text
            vehicle_type = soup.find("span", {"id": "ContentPlaceHolder1_lblVehicleType"}).text
            vehicle_make = soup.find("span", {"id": "ContentPlaceHolder1_lblVehicleMake"}).text
            vehicle_model = soup.find("span", {"id": "ContentPlaceHolder1_lblVehicleModel"}).text
            color = soup.find("span", {"id": "ContentPlaceHolder1_lblColor"}).text
            chassis_number = soup.find("span", {"id": "ContentPlaceHolder1_lblChasisNo"}).text
            issue_date = soup.find("span", {"id": "ContentPlaceHolder1_lblIssueDate"}).text
            expiry_date = soup.find("span", {"id": "ContentPlaceHolder1_lblExpiryDate"}).text
            license_status = soup.find("span", {"id": "ContentPlaceHolder1_lblStatus"}).text
            upload_date = soup.find("span", {"id": "ContentPlaceHolder1_lblDateUploaded"}).text
            upload_time = soup.find("span", {"id": "ContentPlaceHolder1_lblTimeUploaded"}).text

            # Format the data as JSON
            result = {
                "PolicyNumber": policy_number,
                "NewRegistrationNumber": new_registration_number,
                "RegistrationNumber": registration_number,
                "TypeOfCover": type_of_cover,
                "VehicleType": vehicle_type,
                "VehicleMake": vehicle_make,
                "VehicleModel": vehicle_model,
                "Color": color,
                "ChassisNumber": chassis_number,
                "IssueDate": issue_date,
                "ExpiryDate": expiry_date,
                "LicenseStatus": license_status,
                "UploadDate": upload_date,
                "UploadTime": upload_time
            }
            return result

    # def close_driver(self):
    #     self.driver.quit()

    def run(self):
        try:
            data = self.extract_data()
            if data == "Your Policy has expired !!!!":
                return {"status": "failure", "data": data}
            return {"status": "success", "data": data}
        except Exception as e:
            print(e)
        # finally:
        #     self.close_driver()


