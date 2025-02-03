
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TypedDict


# Data class for storing the results of a market price analysis.
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