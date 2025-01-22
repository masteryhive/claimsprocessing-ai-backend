import asyncio
import base64
import os
import re
from playwright.async_api import async_playwright,Playwright,Page,BrowserContext,expect
from bs4 import BeautifulSoup
from src.error_trace.errorlogger import system_logger


class InsuranceDataExtractor:

    def __init__(self, registration_number: str):
        self.registration_number = registration_number
        self.url = "https://www.askniid.org/VerifyPolicy.aspx"

    async def _perform_extraction(self, page:Page):
        await page.goto(self.url)
        await page.locator("#ContentPlaceHolder1_drpOption").select_option("Single")
        await page.locator("#ContentPlaceHolder1_rblNumber_1").click()
        await page.locator("#ContentPlaceHolder1_txtNumber").fill(self.registration_number)
        await asyncio.sleep(2)
        # await page.locator("#ContentPlaceHolder1_btnSearch").click()
        await expect(page.locator("#ContentPlaceHolder1_btnSearch")).to_be_visible()
        await page.locator("#ContentPlaceHolder1_btnSearch").click(timeout=60000)
        await page.wait_for_load_state("networkidle")  # Wait for network activity to settle
        await asyncio.sleep(5)
        # Capture into Image
        screenshot_bytes = await page.screenshot()
        system_logger.info(message=base64.b64encode(screenshot_bytes).decode())

        try:
            await page.locator("#ContentPlaceHolder1_lblPolicyNo").is_visible()
            soup = BeautifulSoup(await page.content(), "html.parser")
            result = {
                "PolicyNumber": soup.find("span", {"id": "ContentPlaceHolder1_lblPolicyNo"}).text,
                "NewRegistrationNumber": soup.find("span", {"id": "ContentPlaceHolder1_lblNewRegistrationNo"}).text,
                "RegistrationNumber": soup.find("span", {"id": "ContentPlaceHolder1_lblRegistrationNo"}).text,
                "TypeOfCover": soup.find("span", {"id": "ContentPlaceHolder1_lblTypeOfCover"}).text,
                "VehicleType": soup.find("span", {"id": "ContentPlaceHolder1_lblVehicleType"}).text,
                "VehicleMake": soup.find("span", {"id": "ContentPlaceHolder1_lblVehicleMake"}).text,
                "VehicleModel": soup.find("span", {"id": "ContentPlaceHolder1_lblVehicleModel"}).text,
                "Color": soup.find("span", {"id": "ContentPlaceHolder1_lblColor"}).text,
                "ChassisNumber": soup.find("span", {"id": "ContentPlaceHolder1_lblChasisNo"}).text,
                "IssueDate": soup.find("span", {"id": "ContentPlaceHolder1_lblIssueDate"}).text,
                "ExpiryDate": soup.find("span", {"id": "ContentPlaceHolder1_lblExpiryDate"}).text,
                "LicenseStatus": soup.find("span", {"id": "ContentPlaceHolder1_lblStatus"}).text,
                "UploadDate": soup.find("span", {"id": "ContentPlaceHolder1_lblDateUploaded"}).text,
                "UploadTime": soup.find("span", {"id": "ContentPlaceHolder1_lblTimeUploaded"}).text
            }
            return result
        except:
            await page.locator("#ContentPlaceHolder1_Div1").is_visible()
            soup = BeautifulSoup(await page.content(), "html.parser")
            policy_state = soup.find("span", {"id": "ContentPlaceHolder1_lblinfo"}).text
            return policy_state

    async def run(self)->dict:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            try:
                page = await context.new_page()
                data = await self._perform_extraction(page)
                if data == "Your Policy has expired !!!!":
                    return {"status": "failure", "data": data}
                return {"status": "success", "data": data}
            except Exception as e:
                system_logger.error(error=f"Error during extraction: {str(e)}")
                return {"status": "error", "data": None}
            finally:
                # dispose context once it is no longer needed.
                await context.close()



