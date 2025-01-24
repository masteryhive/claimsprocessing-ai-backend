# src/interfaces/_base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from typing_extensions import TypedDict

class MarketData(TypedDict):
    prices: List[float]
    metadata: Dict[str, Any]
    
@dataclass
class PriceAnalysis:
    is_realistic: bool
    mean_price: float
    median_price: float
    std_dev: float
    z_score: float
    percentile: float
    is_outlier: bool
    price_range: Dict[str, float]
    thresholds_used: Dict[str, float] = field(default_factory=dict)

class IBrowser(ABC):
    @abstractmethod
    async def initialize(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def cleanup(self) -> None:
        pass
    
    @abstractmethod
    async def _perform_login(self, page: Any) -> bool:
        raise NotImplementedError

class IPriceAnalyzer(ABC):
    @abstractmethod
    def analyze_price_realism(self, market_prices: List[float], quoted_price: float) -> PriceAnalysis:
        pass
    
    @abstractmethod
    def get_expected_price_range(self, prices: List[float]) -> str:
        pass

class IMarketDataFetcher(ABC):
    @abstractmethod
    async def fetch_market_data(self, page: Any, search_term: str) -> MarketData:
        pass