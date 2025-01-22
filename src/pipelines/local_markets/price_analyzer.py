from ._base import IPriceAnalyzer, PriceAnalysis
from typing import List
import numpy as np

class PriceAnalyzer(IPriceAnalyzer):
    def __init__(self, outlier_threshold: float = 1.5,z_threshold=2, iqr_threshold=1.5):
        self.outlier_threshold = outlier_threshold
        self.iqr_threshold = iqr_threshold
        self.z_threshold=z_threshold

    def _remove_outliers(self, prices: List[float]) -> List[float]:
        prices_array = np.array(prices)
        q1 = np.percentile(prices_array, 25)
        q3 = np.percentile(prices_array, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - (self.outlier_threshold * iqr)
        upper_bound = q3 + (self.outlier_threshold * iqr)
        
        return [x for x in prices if lower_bound <= x <= upper_bound]

    def analyze_price_realism(self, market_prices: List[float], quoted_price: float) -> PriceAnalysis:
        prices = np.array(self._remove_outliers(market_prices))
        
        mean_price = np.mean(prices)
        median_price = np.median(prices)
        std_dev = np.std(prices)
        
        z_score = (quoted_price - mean_price) / std_dev if std_dev != 0 else 0
        percentile = np.sum(prices <= quoted_price) / len(prices) * 100
        
        q1, q3 = np.percentile(prices, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - self.iqr_threshold * iqr
        upper_bound = q3 + self.iqr_threshold * iqr
        
        is_outlier = quoted_price < lower_bound or quoted_price > upper_bound
        is_realistic = abs(z_score) < self.z_threshold if std_dev != 0 else True
        
        return PriceAnalysis(
            is_realistic=is_realistic,
            mean_price=mean_price,
            median_price=median_price,
            std_dev=std_dev,
            z_score=z_score,
            percentile=percentile,
            is_outlier=is_outlier,
            price_range={"lower_bound": lower_bound, "upper_bound": upper_bound}
        )

    def get_expected_price_range(self, prices: List[float]) -> str:
        cleaned_prices = self._remove_outliers(prices)
        if not cleaned_prices:
            return "Not enough valid data to determine the price range."
            
        prices_array = np.array(cleaned_prices)
        q1, q3 = np.percentile(prices_array, [25, 75])
        return f"{int(q1):,} - {int(q3):,}"