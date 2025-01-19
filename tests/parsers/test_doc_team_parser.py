import pytest

# Function imports
from src.parsers.doc_team_parser import extract_from_claim_processing

# Test data
@pytest.fixture
def sample_claim_text():
    return """Claim Processing Summary - ID: None
This claim tells the story of Ayo Samuel, policy number ZG/P/1000/010101/22/000346, who experienced a frustrating incident while driving his son to school. Another driver made an abrupt U-turn, resulting in a collision that damaged Ayo's blue 2019 Hyundai SUV, registration number LND 242 JC.

Claim Document Processing Summary:
 - Type of incident: Accident
 - Policy Holder: Ayo Samuel
 - Policy Number: ZG/P/1000/010101/22/000346
 - Vehicle: Hyundai SUV, Registration Number: LND 242 JC
 - Evidence Provided: 
 - Photo of damaged vehicle showing damage to the driver-side door, mirror, and potential paint cracking.
 - Invoice (Number 0050, dated 30th November 2024) from an auto repair shop detailing the cost of repairs.

Summary of Findings:
Ayo's claim includes a photograph and an invoice for ₦268,000 detailing the necessary repairs. The invoice covers the replacement of the driver's side mirror, partial oven-baked painting, bumper clips, miscellaneous parts, and labor costs. The damage description in the claim aligns with the visual evidence in the photograph. However, there's a discrepancy: the invoice is issued to "Franklin Doe," not Ayo Samuel.

Recommendations:
While the claim appears generally valid, it's crucial to address the name discrepancy on the invoice."""

def test_claim_processing_complete(sample_claim_text):
    result = extract_from_claim_processing(sample_claim_text)
    # Test basic claim details
    assert result["typeOfIncident"] == "Accident"
    
    # Test evidence provided
    assert len(result["evidenceProvided"]) == 2
    assert any("Photo of damaged vehicle" in evidence for evidence in result["evidenceProvided"])
    assert any("Invoice" in evidence for evidence in result["evidenceProvided"])

    assert isinstance(result["discoveries"],list)
    assert result["discoveries"] == ['Ayo\'s claim includes a photograph and an invoice for ₦268,000 detailing the necessary repairs. The invoice covers the replacement of the driver\'s side mirror, partial oven-baked painting, bumper clips, miscellaneous parts, and labor costs. The damage description in the claim aligns with the visual evidence in the photograph. However, there\'s a discrepancy: the invoice is issued to "Franklin Doe," not Ayo Samuel.']
    
def test_claim_processing_missing_sections():
    # Test with minimal data
    minimal_text = """Claim Processing Summary - ID: None
    Type of incident: Accident
    - Evidence Provided: 
    - Photo of damaged vehicle showing damage to the driver-side door, mirror, and potential paint cracking.
    - Invoice (Number 0050, dated 30th November 2024) from an auto repair shop detailing the cost of repairs.
    Summary of Findings:
    Ayo's claim includes a photograph and an invoice for ₦268,000 detailing the necessary repairs. The invoice covers the replacement of the driver's side mirror, partial oven-baked painting, bumper clips, miscellaneous parts, and labor costs. The damage description in the claim aligns with the visual evidence in the photograph. However, there's a discrepancy: the invoice is issued to "Franklin Doe," not Ayo Samuel."""

    result = extract_from_claim_processing(minimal_text)
    
    assert result["typeOfIncident"] == "Accident"
    assert result["evidenceProvided"] == ['Photo of damaged vehicle showing damage to the driver-side door, mirror, and potential paint cracking.', 'Invoice (Number 0050, dated 30th November 2024) from an auto repair shop detailing the cost of repairs.']

