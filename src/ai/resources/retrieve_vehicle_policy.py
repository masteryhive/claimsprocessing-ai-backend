from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import time

class InsuranceDataExtractor:
    def __init__(self, registration_number):
        self.registration_number = registration_number

        # Set up Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")  # Optional for some environments
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)  
        
        # Set up Firefox options for headless mode
        # firefox_options = Options()
        # firefox_options.add_argument("--headless")
        
        # self.driver = webdriver.Firefox(options=firefox_options)
        self.url = "https://www.askniid.org/VerifyPolicy.aspx"

    def extract_data(self):
        # Navigate to the website
        self.driver.get(self.url)

        # Interact with the dropdown
        dropdown = Select(self.driver.find_element(By.ID, "ContentPlaceHolder1_drpOption"))
        dropdown.select_by_value("Single")

        # Select the radio button
        radio_button = self.driver.find_element(By.ID, "ContentPlaceHolder1_rblNumber_1")
        radio_button.click()

        # Enter the registration number
        registration_number_input = self.driver.find_element(By.ID, "ContentPlaceHolder1_txtNumber")
        registration_number_input.send_keys(self.registration_number)

        # Click the search button
        search_button = self.driver.find_element(By.ID, "ContentPlaceHolder1_btnSearch")
        search_button.click()

        # Wait for the page to load the results
        time.sleep(3)  # Adjust the delay as needed

        # Get the page content and parse it with BeautifulSoup
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

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
        # Close the WebDriver
        self.driver.quit()


# if __name__ == "__main__":
#     # Assuming the class is named `InsuranceDataExtractor`
#     extractor = InsuranceDataExtractor("LND357JC")
#     try:
#         # Call the method to perform the extraction
#         print(extractor.extract_data())
#     finally:
#         # Ensure the driver is closed after extraction
#         extractor.close_driver()

