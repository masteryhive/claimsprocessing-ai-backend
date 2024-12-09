from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

class InsuranceDataExtractor:
    def __init__(self, registration_number):
        self.registration_number = registration_number
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.109 Safari/537.36"
        )
        self.driver = webdriver.Chrome(options=chrome_options)
        self.url = "https://www.askniid.org/VerifyPolicy.aspx"

    def extract_data(self):
        self.driver.get(self.url)

        dropdown = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_drpOption"))
        )
        dropdown = Select(dropdown)
        dropdown.select_by_value("Single")

        radio_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_rblNumber_1"))
        )
        radio_button.click()

        registration_number_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "ContentPlaceHolder1_txtNumber"))
        )
        registration_number_input.send_keys(self.registration_number)

        search_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "ContentPlaceHolder1_btnSearch"))
        )
        search_button.click()

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_lblPolicyNo"))
        )

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        # Extract and return the required data
            # Extract the data
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

    def close_driver(self):
        self.driver.quit()

    def run(self):
        try:
            data = self.extract_data()
        finally:
            self.close_driver()
        return {"status": "success", "data": data}