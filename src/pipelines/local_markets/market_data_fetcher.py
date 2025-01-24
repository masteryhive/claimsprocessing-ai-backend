import base64,asyncio
from src.pipelines.local_markets._base import IMarketDataFetcher, MarketData
from bs4 import BeautifulSoup
from playwright.async_api import Page, expect
from src.error_trace.errorlogger import system_logger
from typing import List
from uuid import uuid4

class JijiMarketDataFetcher(IMarketDataFetcher):
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    async def fetch_market_data(self, page: Page, search_term: str) -> MarketData:
        try:
            search_term = search_term.replace(" ", "%20")
            search_url = f"https://jiji.ng/lagos/search?query={search_term}&filter_id_verify=Verified%20sellers&sort=new"
            await page.goto(search_url)
            await page.wait_for_load_state('load')
            await asyncio.sleep(2)
            try:
                await expect(page.get_by_text("Search in categories", exact=True)).to_be_visible()
                # Capture into Image
                # await page.screenshot(path=f"webpage_{str(uuid4().hex)}.png")
                # screenshot_bytes = await page.locator(page.get_by_text("Search in categories")).screenshot()
                # system_logger.info(message=base64.b64encode(screenshot_bytes).decode())
                # await asyncio.sleep(2)
                soup = BeautifulSoup(await page.content(), "html.parser")
                price_elements = soup.find_all("div", {"class": "qa-advert-price"})[:50]

                prices = []
                for element in price_elements:
                    price_text = element.text
                    cleaned_price = "".join(char for char in price_text if char.isdigit())
                    try:
                        prices.append(float(cleaned_price))
                    except ValueError:
                        continue
                marketData = MarketData(prices=prices)
         
                return marketData
            except Exception as e:
                await expect(page.get_by_text("Unfortunately, we did not find anything that matches these criteria.", exact=True)).to_be_visible()
                return "Unfortunately, the local market could not find prices for this search.\n Try another keyword combination perhaps use more direct vehicle terms e.g Hyundai Sonata instead of Hyundai SUV"
        except Exception as e:
            system_logger.error(f"Market data fetch failed: {e}")
            return []