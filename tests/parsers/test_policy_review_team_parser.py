import pytest
import re

# Function imports
from src.parsers.policy_review_team_parser import extract_from_policy_details


# Test data
@pytest.fixture
def sample_policy_text():
    return """Policy Review Summary
We've completed our review of Mr. Ayo Samuel's policy coverage for his recent claim concerning damage to his Hyundai SUV.

Policy Details Summary:
 - Coverage Type: Comprehensive
Policy Information:
- Cancellation/Modification Terms: 7 days' notice by registered letter
- Refund Policy: Pro-rata refund for the unexpired period
- Claims Requirements: Immediate notification required; Documents: Police report, Photographs of vehicles with registration details, Phone number and address of third party, Third party's vehicle documents and valid insurance certificate; Notification Period: Within 15 days from the date of occurrence; Procedure: Notify the company as soon as possible with full particulars.
- Coverage Details: Limits: Section II-1(a): N3,000,000.00, Section II-1(b): N3,000,000.00, Section III: N50,000.00; Main Coverage: Accidental collision or overturning, Fire, external explosion, self-ignition, lighting, burglary, housebreaking, or theft, Malicious damage, Transit (including loading and unloading), Third-party liability; Repair Limits: N100,000.00
- Exclusions/Limitations: Exclusions: Consequential loss, Mechanical or electrical breakdown, Damage caused by overloading, Damage to the same area more than once, Events beyond carriage limits, Death or injury during employment, Death or injury to non-employees in the vehicle, Damage to insured's property, Damage to bridges, weighbridges, or viaducts, Damage from sparks or ashes (steam vehicles), Damage from boiler explosion, Liability beyond agreement terms, Flood, typhoon, hurricane, volcanic eruption, earthquake, etc., War, hostilities, civil war, etc., Nuclear weapons material, Ionizing radiation or contamination by radioactivity, Pre-existing damage, Damage or loss involving employees or those driving with insured's permission while under the influence of alcohol or drugs; Geographic Limits: Nigeria
- Key Terms/Conditions: Conditions: Cooling-off period of 14 days, Insurer may choose to pay, repair, or replace, Insurer's liability limited to market value or insured's estimate, Insurer may cover reasonable removal and delivery costs, Insured may authorize repairs within authorized repair limit, Detailed cost estimate required for repairs; Endorsements: []; Special Clauses: License clause, Abandonment clause, Jurisdiction clause, Fire extinguisher clause, Spare parts endorsement, Constructive total loss clause, Pair or set clause, Total loss settlement on pre-accident value basis, Authorized repair limit clause, Multiple claims penalty condition, Motor accessories clause, Intoxicating liquors or drugs warranty, Depreciation in estimate of value, Automatic reduction in total loss payment, Maintenance garage clause, Salvage retrieval clause, Betterment clause, Naked light warranty, Penalty clause, Pre-inception or renewal damage exclusion clause, Subrogation clause; Warranties: Learner driver warranty, Vehicle identification number (VIN) warranty, Claims notification warranty
- Policy Basics: Period: From 2024-11-16 to 2025-11-15; Type: Comprehensive; Policyholder: Ayo Samuel; Premium: Annual: ₦180,000.00, Paid: ₦180,000.00
- Vehicle Details: Make/Model/Year: Hyundai SUV; Value Insured: ₦4,000,000.00

- Policy Status: Active

Mr. Samuel's comprehensive policy is active and covers accidental collisions.  However, his policy has an authorized repair limit of ₦100,000, while the submitted repair invoice totals ₦268,000. This discrepancy needs to be addressed.  Furthermore, the claim currently lacks confirmation of whether the incident was reported within the required timeframe.  This is crucial for adherence to the policy's claims notification requirement."""

@pytest.fixture
def sample_discoveries():
    return {'typeOfIncident': 'Accident', 'evidenceProvided': ['Photo of damaged vehicle showing damage to the driver-side door, mirror, and potential paint cracking.', 'Invoice (Number 0050, dated 30th November 2024) from an auto repair shop detailing the cost of repairs.'], 'discoveries': ['Ayo\'s claim includes a photograph and an invoice for ₦268,000 detailing the necessary repairs. The invoice covers the replacement of the driver\'s side mirror, partial oven-baked painting, bumper clips, miscellaneous parts, and labor costs. The damage description in the claim aligns with the visual evidence in the photograph. However, there\'s a discrepancy: the invoice is issued to "Franklin Doe," not Ayo Samuel.']}


# Tests for extract_from_policy_details
def test_policy_details_complete(sample_policy_text,sample_discoveries):

    result = extract_from_policy_details(sample_policy_text, sample_discoveries['discoveries'])
    
    assert "Active" in result["coverageStatus"]
    assert "<ul>" in result["policyReview"]
    assert len(result["policyReview"]) >= 1
    assert len(result["discoveries"]) >= 1

def test_policy_details_missing_sections():
    text = """Policy Details Summary:
 - Coverage Type: Comprehensive
Policy Information:
- Cancellation/Modification Terms: 7 days' notice by registered letter
- Refund Policy: Pro-rata refund for the unexpired period
- Claims Requirements: Immediate notification required; Documents: Police report, Photographs of vehicles with registration details, Phone number and address of third party, Third party's vehicle documents and valid insurance certificate; Notification Period: Within 15 days from the date of occurrence; Procedure: Notify the company as soon as possible with full particulars.
- Coverage Details: Limits: Section II-1(a): N3,000,000.00, Section II-1(b): N3,000,000.00, Section III: N50,000.00; Main Coverage: Accidental collision or overturning, Fire, external explosion, self-ignition, lighting, burglary, housebreaking, or theft, Malicious damage, Transit (including loading and unloading), Third-party liability; Repair Limits: N100,000.00
- Exclusions/Limitations: Exclusions: Consequential loss, Mechanical or electrical breakdown, Damage caused by overloading, Damage to the same area more than once, Events beyond carriage limits, Death or injury during employment, Death or injury to non-employees in the vehicle, Damage to insured's property, Damage to bridges, weighbridges, or viaducts, Damage from sparks or ashes (steam vehicles), Damage from boiler explosion, Liability beyond agreement terms, Flood, typhoon, hurricane, volcanic eruption, earthquake, etc., War, hostilities, civil war, etc., Nuclear weapons material, Ionizing radiation or contamination by radioactivity, Pre-existing damage, Damage or loss involving employees or those driving with insured's permission while under the influence of alcohol or drugs; Geographic Limits: Nigeria
- Key Terms/Conditions: Conditions: Cooling-off period of 14 days, Insurer may choose to pay, repair, or replace, Insurer's liability limited to market value or insured's estimate, Insurer may cover reasonable removal and delivery costs, Insured may authorize repairs within authorized repair limit, Detailed cost estimate required for repairs; Endorsements: []; Special Clauses: License clause, Abandonment clause, Jurisdiction clause, Fire extinguisher clause, Spare parts endorsement, Constructive total loss clause, Pair or set clause, Total loss settlement on pre-accident value basis, Authorized repair limit clause, Multiple claims penalty condition, Motor accessories clause, Intoxicating liquors or drugs warranty, Depreciation in estimate of value, Automatic reduction in total loss payment, Maintenance garage clause, Salvage retrieval clause, Betterment clause, Naked light warranty, Penalty clause, Pre-inception or renewal damage exclusion clause, Subrogation clause; Warranties: Learner driver warranty, Vehicle identification number (VIN) warranty, Claims notification warranty
- Policy Basics: Period: From 2024-11-16 to 2025-11-15; Type: Comprehensive; Policyholder: Ayo Samuel; Premium: Annual: ₦180,000.00, Paid: ₦180,000.00
- Vehicle Details: Make/Model/Year: Hyundai SUV; Value Insured: ₦4,000,000.00

- Policy Status: Active"""
    discoveries = []
    result = extract_from_policy_details(text, discoveries)
    
    assert "Active" in result["coverageStatus"]
    assert "<ul>" in result["policyReview"]
    assert len(result["discoveries"]) == 1