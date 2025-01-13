
from langchain_core.tools import tool
from typing import Annotated, Dict, Union


@tool
def determine_settlement_offer_range(
    fairly_used_cost: Annotated[float, "The median cost of fairly-used parts"],
    brand_new_price: Annotated[float, "The median cost of brand new parts"]
) -> dict:
    """
    Calculate the settlement offer range based on the provided costs.
    """
    upper_interval = 1.25 * fairly_used_cost
    lower_interval = 1.25 * brand_new_price
    return {
        "upper_interval": upper_interval,
        "lower_interval": lower_interval
    }

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