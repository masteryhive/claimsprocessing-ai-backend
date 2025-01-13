import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

from playwright.sync_api import sync_playwright
import time

class VehicleVinDataExtractor:
    def __init__(self, vehicle_identification_number: str):
        self.vehicle_identification_number = vehicle_identification_number
        self.playwright = sync_playwright().start()
        
        # Configure browser with Zenrows proxy
        self.browser = self.playwright.chromium.launch(
            headless=False,  # Set to True for production
            proxy={
                "server":"http://superproxy.zenrows.com:1337",
                "username": "T6FrJ4Y9JQCM",  # Replace with your Zenrows API key
                "password": "MxtQA8Rc58OW",
            }
        )
        
        # Create context with specific options and additional headers
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            # extra_http_headers={
            #     "x-zenrows-bypass": "true",  # Enable Javascript rendering
            #    #  "x-zenrows-antibot": "true"   # Enable antibot protection bypass
            # }
        )
        
        self.page = self.context.new_page()
        self.url = "https://www.vindecoderz.com"

    def extract_data(self):
        print()
        self.page.goto(f"{self.url}/EN/check-lookup/{self.vehicle_identification_number}",
                       wait_until="networkidle")
        
        try:
            # Wait for and click checkbox
            self.page.wait_for_selector("input[type='checkbox'], label.cb-lb input[type='checkbox']",
                                        timeout=30000,state="visible")
            self.page.click("input[type='checkbox'], label.cb-lb input[type='checkbox']",force=True)
        except Exception:
            print("Could not find or click the checkbox. Continuing anyway...")

        # Wait for content to load
        self.page.wait_for_load_state('networkidle')
        
        # Extract data using evaluate
        data = self.page.evaluate("""() => {
            const basic_info = {};
            const info_table = document.querySelector('.table.table-hover');
            if (info_table) {
                info_table.querySelectorAll('tr').forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length === 2) {
                        const key = cells[0].querySelector('span')?.textContent.trim().replace(':', '');
                        const value = cells[1].querySelector('span b')?.textContent || cells[1].textContent;
                        if (key) basic_info[key] = value.trim();
                    }
                });
            }

            const recalls = [];
            const recalls_table = document.querySelectorAll('.table.table-striped.table-hover')[0];
            if (recalls_table) {
                recalls_table.querySelectorAll('tr:not(:first-child)').forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 3) {
                        recalls.push({
                            'campaign_number': cells[0].textContent.trim(),
                            'date': cells[1].textContent.trim(),
                            'component': cells[2].textContent.trim()
                        });
                    }
                });
            }

            const problems = [];
            const problems_table = document.querySelectorAll('.table.table-striped.table-hover')[1];
            if (problems_table) {
                problems_table.querySelectorAll('tr:not(:first-child)').forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 3) {
                        problems.push({
                            'issue_id': cells[0].textContent.trim(),
                            'failed_date': cells[1].textContent.trim(),
                            'component': cells[2].textContent.trim()
                        });
                    }
                });
            }

            return {
                basic_info,
                recalls,
                problems
            };
        }""")
        
        return data

    def close_driver(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def run(self):
        try:
            data = self.extract_data()
            if data == "Your Policy has expired !!!!":
                return {"status": "failure", "data": data}
            return {"status": "success", "data": data}
        except Exception as e:
            print(e)
            return {"status": "failure", "data": str(e)}
        finally:
            self.close_driver()

# v = VehicleVinDataExtractor("5NPE34AF1FH095171")
# print(v.extract_data())