from ._base import IMarketDataFetcher
from bs4 import BeautifulSoup
from playwright.async_api import Page, expect
import asyncio
from src.error_trace.errorlogger import system_logger
from typing import List
from uuid import uuid4

class JijiMarketDataFetcher(IMarketDataFetcher):
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    async def fetch_market_data(self, page: Page, search_term: str) -> List[float]:
        try:
            search_term = search_term.replace(" ", "%20")
            search_url = f"https://jiji.ng/lagos/search?query={search_term}&filter_id_verify=Verified%20sellers&sort=new"
            await page.goto(search_url)
            await asyncio.sleep(2)
            await page.screenshot(path=f"webpage_{str(uuid4().hex)}.png")
            try:
                await expect(page.get_by_text("Search in categories", exact=True)).to_be_visible()
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

                return prices
            except Exception as e:
                await expect(page.get_by_text("Unfortunately, we did not find anything that matches these criteria.", exact=True)).to_be_visible()
                return "Unfortunately, the local market could not find prices for this search.\n Try another keyword combination perhaps use more direct vehicle terms e.g Hyundai Sonata instead of Hyundai SUV"
        except Exception as e:
            system_logger.error(f"Market data fetch failed: {e}")
            return []