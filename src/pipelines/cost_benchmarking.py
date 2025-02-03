

from typing import List
from pydantic import BaseModel, Field
from src.pipelines.config import PriceAnalysis
from src.pipelines.price_analysis._price_analyzer import PriceAnalyzer
from src.pipelines.price_analysis.query_engine import get_part_price

#Base Class for Analysis
class AnalysisModel(BaseModel):
    result: str
    priceRange: str = Field(default="no price range")

# Class returns Analysis List 
class AnalysisModelResultList(BaseModel):
    analysisResult: List[AnalysisModel]

class CostBenchmarking():
    """
    A class for benchmarking and analyzing vehicle part costs against market prices.

    This class handles fetching market prices for vehicle parts and analyzing whether
    quoted prices are realistic based on statistical analysis of market data.

    Attributes:
        make (str): The vehicle manufacturer (e.g. "Toyota", "Honda")
        model (str): The vehicle model (e.g. "Camry", "Civic") 
        year (int): The vehicle manufacturing year
        part (str): The specific vehicle part being analyzed
        quoted_price (float): The price being quoted for the part
        analyzer (PriceAnalyzer): Instance of PriceAnalyzer for statistical analysis

    Methods:
        _fetch_query(): Fetches market price data for the specified part
        _format_analysis_result(): Formats the analysis results into a readable string
        run_analysis(): Performs the full price analysis workflow
    """
    def __init__(self, make:str, model:str,body_type:str, year:int, part:str, quoted_price:float, condition:str="brand new") -> None:
        """
        Initialize a new CostBenchmarking instance.

        Args:
            make (str): Vehicle manufacturer name
            model (str): Vehicle model name
            year (int): Vehicle manufacturing year
            part (str): Vehicle part name
            quoted_price (float): Price being quoted for analysis
            condition (str): Part condition - "brand new" or "fairly used". Defaults to "brand new"
        """
        self.make = make
        self.model = model
        self.year = year
        self.part = part
        self.body_type=body_type
        self.condition = condition
        self.quoted_price = quoted_price
        self.analyzer = PriceAnalyzer()

    def _fetch_query(self)->int:
        """
        Fetch the market price for the specified vehicle part.

        Returns:
            dict: Contains the market price data for the part
        """
        return get_part_price(self.make, self.model,self.body_type, int(self.year),self.part, self.condition)
    
    def _format_analysis_result(self, analysis: PriceAnalysis, quoted_price: float) -> str:
        """
        Format the price analysis results into a human-readable string.

        Args:
            analysis (PriceAnalysis): The analysis results object
            quoted_price (float): The price being analyzed

        Returns:
            str: Formatted analysis results with price comparisons and status
        """
        status = "✅ This quoted price appears REALISTIC" if analysis.is_realistic else "❌ This quoted price appears UNREALISTIC"
        
        return (
            f"\nAnalysis for quoted price: {quoted_price:,.0f}\n"
            "--------------------------------------------------------------\n"
            f"median_price: {analysis.median_price:,.2f}\n"
            f"realistic_price_range: {analysis.price_range['lower_bound']:,.0f} "
            f"to {analysis.price_range['upper_bound']:,.0f}\n"
            f"quoted_price_percentile: {analysis.percentile:.1f}th percentile\n"
            f"status: {status}"
        )
    
    def run_analysis(self):
        """
        Execute the complete price analysis workflow.

        This method:
        1. Fetches current market price data
        2. Calculates a price interval around the market price
        3. Analyzes the quoted price against this interval
        4. Formats and returns the analysis results

        Returns:
            AnalysisModel: Contains the formatted analysis results and price range
        """
        price = self._fetch_query()
        if isinstance(price,dict) == False:
            return AnalysisModel(result="no result")
        price = price['price']
        marketdata_interval = [price+(price*0.05),price-(price*0.05)]
        price_range = self.analyzer.get_expected_price_range(marketdata_interval)
        analysis = self.analyzer.analyze_price_realism(marketdata_interval, self.quoted_price)
        final_result = self._format_analysis_result(analysis, self.quoted_price)
        return AnalysisModel(result=final_result, priceRange=price_range)