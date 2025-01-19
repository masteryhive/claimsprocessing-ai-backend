import pytest
import re

# Function imports
from src.parsers.settlement_team_parser import  extract_from_settlement_offer

# Test data
@pytest.fixture
def sample_settlement_text():
    return """This is a settlement offer.
    We propose $5000 in compensation.
    Justification: The damage was extensive and repairs are necessary."""

@pytest.fixture
def sample_fraud_text():
    return """PreLoss Comparison: Previous claims show consistent patterns
    Property values align with expectations

Fraud Risk Assessment:
Fraud Threshold score: 75
Overall Fraud Risk Level: Medium

Recommendations:
1. Verify documentation
2. Contact previous insurers"""

@pytest.fixture
def sample_claim_text():
    return """Type of incident: Water Damage
    
Evidence Provided:
- Photos of damaged ceiling
- Plumber's report
- Water bill showing spike

Summary of Findings:
Leak confirmed from upper floor.
Significant water damage present.

Recommendations:
Proceed with claim."""

@pytest.fixture
def sample_policy_text():
    return """Coverage Status: Active and Valid

Policy Details Summary:
- Premium: $1200/year
- Coverage Limit: $500,000
- Deductible: $1000

    - Policy Status: In Force"""

# Tests for extract_from_settlement_offer
def test_settlement_offer_with_justification(sample_settlement_text):
    discoveries = ["Previous finding 1", "Previous finding 2"]
    result = extract_from_settlement_offer(sample_settlement_text, discoveries)
    
    assert "settlementOffer" in result
    assert "discoveries" in result
    assert "The damage was extensive and repairs are necessary" in result["discoveries"]
    assert len(result["discoveries"]) == len(discoveries) + 1
    assert "<br/>" in result["settlementOffer"]

def test_settlement_offer_without_justification():
    text = "This is a settlement offer without justification."
    discoveries = ["Previous finding"]
    result = extract_from_settlement_offer(text, discoveries)
    
    assert result["settlementOffer"] == text
    assert len(result["discoveries"]) == len(discoveries) + 1
    assert result["discoveries"][0] == ""
