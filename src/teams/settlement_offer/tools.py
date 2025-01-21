
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from langchain_core.tools import tool
from typing import Annotated, Dict, TypeGuard, Union
from src.error_trace.errorlogger import system_logger


# Custom Exceptions
class SettlementCalculationError(Exception):
    """Base exception for settlement calculation errors"""
    pass

class InvalidCostError(SettlementCalculationError):
    """Raised when cost values are invalid"""
    pass

class NegativeCostError(InvalidCostError):
    """Raised when cost values are negative"""
    pass


# Configuration
@dataclass
class SettlementConfig:
    MARKUP_FACTOR: Decimal = Decimal('1.25')
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 0.5  # seconds
    MAX_COST_THRESHOLD: Decimal = Decimal('1000000')  # Arbitrary high value to prevent unreasonable calculations

def validate_positive_decimal(value: Union[float, Decimal]) -> TypeGuard[Decimal]:
    """Validate and convert input to positive Decimal"""
    try:
        decimal_value = Decimal(str(value))
        if decimal_value <= 0:
            raise NegativeCostError(f"Cost must be positive, got: {value}")
        if decimal_value > SettlementConfig.MAX_COST_THRESHOLD:
            raise InvalidCostError(f"Cost exceeds maximum threshold: {value}")
        return True
    except InvalidOperation:
        raise InvalidCostError(f"Invalid cost value: {value}")


# @tool
# def determine_settlement_offer_range(
#     fairly_used_cost: Annotated[float, "The median cost of fairly-used parts"],
#     brand_new_price: Annotated[float, "The median cost of brand new parts"]
# ) -> dict:
#     """
#     Calculate the settlement offer range based on the provided costs.
#     """
#     upper_interval = 1.25 * fairly_used_cost
#     lower_interval = 1.25 * brand_new_price
#     return {
#         "upper_interval": upper_interval,
#         "lower_interval": lower_interval
#     }

@tool
def determine_settlement_offer_range(
    fairly_used_cost: Annotated[float, "The median cost of fairly-used parts"],
    brand_new_price: Annotated[float, "The median cost of brand new parts"]
) -> Dict[str, Decimal]:
    """
    Calculate the settlement offer range based on the provided costs.
    
    Args:
        fairly_used_cost: The median cost of fairly-used parts
        brand_new_price: The median cost of brand new parts
        
    Returns:
        Dict containing upper and lower interval values as Decimals
        
    Raises:
        InvalidCostError: If costs are invalid or exceed threshold
        NegativeCostError: If costs are negative
        SettlementCalculationError: For other calculation errors
    """
    try:

        # Validate inputs
        validate_positive_decimal(fairly_used_cost)
        validate_positive_decimal(brand_new_price)
        
        # Convert to Decimal for precise calculations
        used_cost_decimal = Decimal(str(fairly_used_cost))
        new_price_decimal = Decimal(str(brand_new_price))
        
        # Calculate intervals
        upper_interval = used_cost_decimal * SettlementConfig.MARKUP_FACTOR
        lower_interval = new_price_decimal * SettlementConfig.MARKUP_FACTOR
        
        result = {
            "upper_interval": upper_interval.quantize(Decimal('0.01')),
            "lower_interval": lower_interval.quantize(Decimal('0.01'))
        }
        
        return result
        
    except (InvalidCostError, NegativeCostError) as e:
        system_logger.error(f"Validation error: {str(e)}")
        raise
    except Exception as e:
        system_logger.error(f"Unexpected error in settlement calculation: {str(e)}")
        raise SettlementCalculationError(f"Failed to calculate settlement range: {str(e)}")
    
@tool
def determine_settlement_offer(
    upper_interval_from_settlement_range: Annotated[float, "The price for the upper interval settlement range"],
    lower_interval_from_settlement_range: Annotated[float, "The price for the lower interval settlement range"],
    the_total_cost_from_the_invoice: Annotated[float, "The invoice total cost"]
) -> str:
    """
    Determine the appropriate settlement offer based on the provided settlement range and invoice total cost.

    This tool calculates the settlement offer by comparing the total cost from the invoice with the given settlement range.
    If the total cost falls within the range, it is used as the settlement offer. Otherwise, the average of the upper and lower
    interval from the settlement range is used.

    Parameters:
    upper_interval_from_settlement_range (float): The price for the upper interval settlement range.
    lower_interval_from_settlement_range (float): The price for the lower interval settlement range.
    the_total_cost_from_the_invoice (float): The invoice total cost.

    Returns:
    str: A formatted string indicating the calculated settlement offer.
    """
    if lower_interval_from_settlement_range <= the_total_cost_from_the_invoice <= upper_interval_from_settlement_range:
        settlement_offer = the_total_cost_from_the_invoice
    else:
        settlement_offer = (upper_interval_from_settlement_range + lower_interval_from_settlement_range) / 2

    return f"Settlement Offer: ₦{settlement_offer}"