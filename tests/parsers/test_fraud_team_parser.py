import pytest
import re

# Function imports
from src.parsers.fraud_team_parser import extract_from_fraud_checks

@pytest.fixture
def sample_fraud_text():
    return """Fraud Detection Report - ID: null
Policy Review Summary
We've completed our review of Mr. Samuel's policy coverage for his recent claim.  There are several discrepancies that require attention before the claim can proceed. The claim was reported on January 21, 2025, exceeding the 15-day notification period stipulated in the policy.  Additionally, the repair costs of ₦268,000 exceed the authorized repair limit of ₦100,000.  This means that even if the claim were deemed valid, the payout would be capped at ₦100,000. The missing registration number on the policy document needs to be addressed and updated with the provided registration LND 242 JC. The chassis number provided by claimant does not match NIID records and Vehicle is not insured by NIID.

Fraud Investigation Details:
- Fraud Threshold score: 50
- Damaged Part Repair Price From Local Market: 
  - Marginal Price for Fairly-used parts: null
  - Marginal Price for Brand Ne parts: null
- Key Concerns Identified: Vehicle Data Mismatch, Vehicle not insured by NIID, Repair cost exceeds authorized limit (₦268,000 > ₦100,000), Late claim filing (21 January 2025, exceeding the 15-day notification period), Invoice provided is for "Franklin Doe," not the claimant "Ayo Samuel."

PreLoss Comparison:
- Vehicle Damage Analysis:
  - Pre-existing Damages: None
  - New Damages Claimed: None
  - Overlap Analysis:
    - Verified Pre-existing Damages: None
    - Legitimate New Damages: None
    - Damages That will be considered for this claim: None


Fraud Risk Assessment:
- Risk Scoring Matrix:
  - Fraud Risk Score: 50
  - Scoring Method:
    - First Red Flag Threshold: 50
  - Overall Fraud Risk Level: HIGH

- Detailed Risk Indicators:
  - Critical Flags:
    - Vehicle Data Mismatch: The chassis number provided by claimant does not match NIID records.
    - Insured By NIID: Vehicle is not insured by NIID.

  - Amber Flags:
    - Repair cost exceeds authorized limit (₦268,000 > ₦100,000).
    - Late claim filing (21 January 2025, exceeding the 15-day notification period).
    - Invoice provided is for "Franklin Doe," not the claimant "Ayo Samuel."


Investigative Findings:
- Key Observations: Presence of critical red flags related to vehicle data mismatch and NIID insurance status. Additional amber flags raise concerns about the claim's legitimacy.

- Critical Red Flags:
  - Vehicle data mismatch between claimant-provided information and NIID records.
  - Vehicle not insured by NIID.

Overall Fraud Risk Level: HIGH
- Fraud Score: 50

Recommendations:
Initiate a thorough investigation into the discrepancies identified. Contact the claimant for clarification on the mismatched chassis number and the lack of NIID insurance. Request additional documentation, such as a police report and the claimant's insurance certificate.  Verify the legitimacy of the repair invoice and the relationship between the claimant and "Franklin Doe."  Escalate the case to the Special Investigative Unit (SIU) for further review.  Suspend any claim payments until the investigation is complete."""


# Tests for extract_from_fraud_checks
def test_fraud_checks_complete(sample_fraud_text):
    discoveries = ["Previous discovery"]
    result = extract_from_fraud_checks(sample_fraud_text, discoveries)
    
    assert "preLossComparison" in result
    assert "discoveries" in result

def test_fraud_checks_missing_sections():
    text = "PreLoss Comparison: Some data\n\nOverall Fraud Risk Level: Low"
    discoveries = []
    result = extract_from_fraud_checks(text, discoveries)
    
    assert "- Risk Level" in "".join(result["discoveries"])
    assert isinstance(result["discoveries"],list)
 
