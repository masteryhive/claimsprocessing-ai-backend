from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict
from src.config.appconfig import env_config
from src.pipelines.config import PriceAnalysis

# Interface for market price analysis.
class IMarketPriceAnalyzer(ABC):
    @abstractmethod
    def analyze_price_realism(
        self, market_prices: List[float], quoted_price: float
    ) -> PriceAnalysis:
        pass

    @abstractmethod
    def get_expected_price_range(self, prices: List[float]) -> str:
        pass
