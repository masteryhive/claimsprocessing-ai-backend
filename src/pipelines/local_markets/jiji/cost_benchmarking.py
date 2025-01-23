import asyncio
from src.pipelines.local_markets._base import IBrowser, IPriceAnalyzer, IMarketDataFetcher, PriceAnalysis
from src.pipelines.local_markets.jiji.playwright_browser import PlaywrightBrowser
from src.pipelines.local_markets.price_analyzer import PriceAnalyzer
from src.pipelines.local_markets.market_data_fetcher import JijiMarketDataFetcher
from typing import Optional, Dict, Any

class CostBenchmarking:
    def __init__(
        self,
        email: str,
        password: str,
        browser: Optional[IBrowser] = None,
        analyzer: Optional[IPriceAnalyzer] = None,
        fetcher: Optional[IMarketDataFetcher] = None,
        timeout: int = 30
    ):
        self.browser = browser or PlaywrightBrowser(email, password, timeout)
        self.analyzer = analyzer or PriceAnalyzer()
        self.fetcher = fetcher or JijiMarketDataFetcher(timeout)

    async def __aenter__(self):
        await self.browser.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.cleanup()

    def format_analysis_result(self, analysis: PriceAnalysis, quoted_price: float) -> str:
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
        
        page = await self.browser.context.new_page()
        await self.browser.login(page)
        market_prices = await self.fetcher.fetch_market_data(page, search_term)
        if not market_prices:
            return "Unable to fetch market prices"
            
        analysis = self.analyzer.analyze_price_realism(market_prices, quoted_price)
        await self.browser.cleanup()
        return self.format_analysis_result(analysis, quoted_price)


# async def main():
#     async with CostBenchmarking(
#         email="sam@masteryhive.ai",
#         password="JLg8m4aQ8n46nhC"
#     ) as benchmarking:
#         result = await benchmarking.analyze_market_price(
#             "hyundai sonata side mirror tokunbo",
#             49000
#         )
#         print(result)
    
# asyncio.run(main())