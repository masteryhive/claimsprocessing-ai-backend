import pytest
import re

# Function imports
from src.parsers.settlement_team_parser import  extract_from_settlement_offer

# Test data
@pytest.fixture
def sample_settlement_text():
    return """Settlement Offer: ₦0.0
Settlement Offer Reason: ❌ Several discrepancies and inconsistencies raise red flags, including a significant difference between the claimed amount and the market analysis, an inactive policy, mismatched names and vehicle details, leading to a recommendation for a fraud investigation.
Settlement Range: ₦0.00 - ₦0.00
Marginal Price for Fairly-used parts: ₦0
Marginal Price for Brand New parts: ₦0
Justification: The market analysis returned a value of ₦0.0 for similar repairs, significantly lower than the claimant's invoice of ₦268,000.  Further investigation is needed due to discrepancies in the claim details and the policy status.  A fraud investigation is highly recommended."""


# Tests for extract_from_settlement_offer
def test_settlement_offer_with_justification(sample_settlement_text):
    discoveries = ["Previous finding 1", "Previous finding 2"]
    result = extract_from_settlement_offer(sample_settlement_text, discoveries)

    assert "settlementOffer" in result
    assert "discoveries" in result
    assert "The market analysis returned a value of ₦0.0 for similar repairs" in result["discoveries"][0]
    assert isinstance(result["discoveries"],list)


def test_settlement_offer_without_justification():
    text = """Settlement Offer: ₦0.0
Settlement Offer Reason: ❌ Several discrepancies and inconsistencies raise red flags, including a significant difference between the claimed amount and the market analysis, an inactive policy, mismatched names and vehicle details, leading to a recommendation for a fraud investigation.
Settlement Range: ₦0.00 - ₦0.00
Marginal Price for Fairly-used parts: ₦0
Marginal Price for Brand New parts: ₦0"""

    discoveries = ["Previous finding"]
    result = extract_from_settlement_offer(text, discoveries)
    print(result)
    assert result["settlementOffer"] == text.replace("\n","<br/>")
    assert isinstance(result["discoveries"],list)

