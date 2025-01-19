import pytest
import re

# Function imports
from src.parsers.fraud_team_parser import extract_from_fraud_checks

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

# Tests for extract_from_fraud_checks
def test_fraud_checks_complete(sample_fraud_text):
    discoveries = ["Previous discovery"]
    result = extract_from_fraud_checks(sample_fraud_text, discoveries)
    
    assert "preLossComparison" in result
    assert "discoveries" in result
    assert "Previous claims show consistent patterns" in result["preLossComparison"]
    assert "Medium" in result["discoveries"][-1]
    assert "75" not in result["discoveries"][-1]  # Fraud score should not be included
    assert "<br/>" in result["preLossComparison"]

def test_fraud_checks_missing_sections():
    text = "PreLoss Comparison: Some data\n\nOverall Fraud Risk Level: Low"
    discoveries = []
    result = extract_from_fraud_checks(text, discoveries)
    
    assert "N/A" in result["discoveries"][-1]
    assert "Some data" in result["preLossComparison"]
