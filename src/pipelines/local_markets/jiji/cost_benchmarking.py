import asyncio
from src.pipelines.local_markets._base import IBrowser, IPriceAnalyzer, IMarketDataFetcher, MarketData, PriceAnalysis
from src.pipelines.local_markets.jiji.playwright_browser import PlaywrightBrowser
from src.pipelines.local_markets.price_analyzer import PriceAnalyzer
from src.pipelines.local_markets.market_data_fetcher import JijiMarketDataFetcher
from typing import List, Optional, Dict, Any
from langchain_core.tools import ToolException

class BrowserPool:
    def __init__(self, browser: IBrowser, max_concurrency: int):
        self.browser = browser
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.active_pages = set()

    async def with_page(self, callback: callable) -> Any:
        async with self.semaphore:
            page = await self.browser.create_authenticated_page()
            self.active_pages.add(page)
            try:
                return await callback(page)
            finally:
                await page.close()
                self.active_pages.remove(page)

class CostBenchmarking:
    def __init__(
        self,
        email: str,
        password: str,
        analyzer: Optional[IPriceAnalyzer] = None,
        fetcher: Optional[IMarketDataFetcher] = None,
        max_concurrency: int = 4
    ):
        self.browser = PlaywrightBrowser(email, password)
        self.pool = BrowserPool(self.browser, max_concurrency)
        self.analyzer = analyzer or PriceAnalyzer()
        self.fetcher = fetcher or JijiMarketDataFetcher()
        
        if max_concurrency < 1:
            raise ValueError("Max concurrency must be at least 1")

    async def __aenter__(self):
        await self.browser.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Close all active pages first
        if self.pool.active_pages:
            await asyncio.gather(*[page.close() for page in self.pool.active_pages])
        # Then cleanup browser
        await self.browser.cleanup()

    async def _fetch_data(self, page: Any, search_term: str) -> MarketData:
        try:
            result = await self.fetcher.fetch_market_data(page, search_term)
            if isinstance(result, str):
                return  "No market prices found"
            return result
        except Exception as e:
            raise ToolException(f"Data fetch failed: {str(e)}") from e
        
    def _format_analysis_result(self, analysis: PriceAnalysis, quoted_price: float) -> str:
        status = "✅ This price appears REALISTIC" if analysis.is_realistic else "❌ This price appears UNREALISTIC"
        
        return (
            f"\nAnalysis for quoted price: {quoted_price:,.0f}\n"
            "--------------------------------------------------------------\n"
            f"median_price: {analysis.median_price:,.2f}\n"
            f"realistic_price_range: {analysis.price_range['lower_bound']:,.0f} "
            f"to {analysis.price_range['upper_bound']:,.0f}\n"
            f"quoted_price_percentile: {analysis.percentile:.1f}th percentile\n"
            f"status: {status}"
        )

    async def analyze_market_price(self, search_term: str, quoted_price: float) -> str:
        async def process(page):
            market_data = await self._fetch_data(page, search_term)
            if isinstance(market_data,str):
                return market_data
            analysis = self.analyzer.analyze_price_realism(market_data.get('prices'), quoted_price)
            return self._format_analysis_result(analysis, quoted_price)
        
        return await self.pool.with_page(process)

    async def concurrent_analyze(self, tasks: List[List]) -> List[str]:
        async def wrapper(search_term, price):
            return await self.analyze_market_price(search_term, price)
        
        return await asyncio.gather(*[
            wrapper(task[0], task[1]) for task in tasks
        ])


# data =   [["hyundai sonata 2015 side mirror fairly used",
#             49000.4],["hyundai sonata 2015 side mirror brand new",
#             49000.4]]
# async def main():
#     async with CostBenchmarking(
#         email="sam@masteryhive.ai",
#         password="JLg8m4aQ8n46nhC",max_concurrency=len(data)
#     ) as benchmarking:
#         result = await benchmarking.concurrent_analyze(
#           data
#         )
#         print(result)
    
# asyncio.run(main())