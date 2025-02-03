import numpy as np
from typing import List

# function to remove outliers
def remove_outliers(prices: List[float], threshold: float = 1.5) -> List[float]:
    """
    Removes outliers from the price list using the IQR method.
    
    Parameters:
    prices (List[float]): List of prices
    threshold (float): Number of IQR ranges to consider for outlier detection
    
    Returns:
    List[float]: Prices with outliers removed
    """
    prices_array = np.array(prices)
    q1 = np.percentile(prices_array, 25)
    q3 = np.percentile(prices_array, 75)
    iqr = q3 - q1
    
    lower_bound = q1 - (threshold * iqr)
    upper_bound = q3 + (threshold * iqr)
    
    return [x for x in prices if lower_bound <= x <= upper_bound]

# function to analyze realistic prices
def analyze_price_realism(market_prices: List[float], quoted_price: float, threshold: float = 1.5) -> dict:
    """
    Analyzes if a quoted price is realistic based on market data using statistical methods.
    
    Parameters:
    market_prices (List[float]): List of known market prices
    quoted_price (float): The price to analyze
    threshold (float): Number of IQR ranges to consider for outlier detection (default 1.5)
    
    Returns:
    dict: Analysis results including whether the price is realistic and supporting statistics
    """
    # Convert to numpy array for statistical calculations
    prices = np.array(market_prices)
    
    # Calculate basic statistics
    median_price = np.median(prices)
    q1 = np.percentile(prices, 25)
    q3 = np.percentile(prices, 75)
    iqr = q3 - q1
    
    # Define bounds for realistic prices
    lower_bound = q1 - (threshold * iqr)
    upper_bound = q3 + (threshold * iqr)
    
    # Calculate percentage difference from median
    percent_diff_from_median = ((quoted_price - median_price) / median_price) * 100
    
    # Determine if price is realistic
    is_realistic = lower_bound <= quoted_price <= upper_bound
    
    # Calculate what percentile the quoted price falls into
    percentile = np.percentile(prices, [0, 25, 50, 75, 100])
    price_percentile = sum(1 for x in prices if x < quoted_price) / len(prices) * 100
    
    return {
        "is_realistic": is_realistic,
        "analysis": {
            "median_price": median_price,
            "price_range": {
                "lower_bound": lower_bound,
                "upper_bound": upper_bound
            },
            "market_statistics": {
                "minimum": np.min(prices),
                "maximum": np.max(prices),
                "q1": q1,
                "q3": q3
            },
            "quoted_price_percentile": price_percentile,
            "percent_difference_from_median": percent_diff_from_median
        }
    }

# function to  check prices 
def check_price(market_prices: List[float], quoted_price: float) -> None:
    """
    Helper function to print a human-readable analysis of the price.
    """
    # First remove outliers
    cleaned_prices = remove_outliers(market_prices)
    
    print(f"\nOriginal number of prices: {len(market_prices)}")
    print(f"Number of prices after removing outliers: {len(cleaned_prices)}")
    
    result = analyze_price_realism(cleaned_prices, quoted_price)
    
    print(f"\nAnalysis for quoted price: {quoted_price:,.0f}")
    print("-" * 50)
    
    if result["is_realistic"]:
        print("✅ This price appears REALISTIC based on market data")
    else:
        print("❌ This price appears UNREALISTIC based on market data")
    
    analysis = result["analysis"]
    print(f"\nMarket Statistics (after removing outliers):")
    print(f"- Median price: {analysis['median_price']:,.0f}")
    print(f"- Realistic price range: {analysis['price_range']['lower_bound']:,.0f} to {analysis['price_range']['upper_bound']:,.0f}")
    print(f"- Your price is in the {analysis['quoted_price_percentile']:.1f}th percentile")
    print(f"- Difference from median: {analysis['percent_difference_from_median']:+.1f}%")

# Your market prices
market_prices = [100000, 75000, 80000, 30000, 8800000, 400000, 75000, 8700000, 
                130000, 55000, 35000, 70000, 80000, 480000, 4500000, 450000, 
                200000, 700000, 800000, 70000, 320000, 250000, 200000]

# Let's see the cleaned data
cleaned_prices = remove_outliers(market_prices)
print("Original prices:", sorted(market_prices))
print("\nPrices after removing outliers:", sorted(cleaned_prices))

check_price(market_prices, 120000)