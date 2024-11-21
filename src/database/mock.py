from datetime import datetime, timedelta
import random
from typing import Dict, List
from pydantic import BaseModel, Field

from src.datamodels.tools import ClaimantData


class PolicyHolderInformation(BaseModel):
    claimant_id: str
    name: str
    contact: str
    address: str = Field(..., description="Address of the policy holder")
    contact_number: str = Field(..., description="Contact number of the policy holder")
    email: str = Field(..., description="Email address of the policy holder")


class VehicleInformation(BaseModel):
    vehicle_make: str = Field(..., description="Make of the vehicle")
    vehicle_model: str = Field(..., description="Model of the vehicle")
    year_of_manufacture: int = Field(
        ..., description="Year the vehicle was manufactured"
    )
    vin: str = Field(..., description="Vehicle Identification Number")
    license_plate_number: str = Field(
        ..., description="License plate number of the vehicle"
    )


class PolicyDetails(BaseModel):
    policy_holder_name: str = Field(..., description="Name of the policy holder")
    policy_start_date: datetime = Field(..., description="Start date of the policy")
    policy_expiry_date: datetime = Field(..., description="Expiry date of the policy")
    policy_status: str = Field(..., description="Current status of the policy")
    coverage_type: str = Field(
        ..., description="Type of coverage provided by the policy"
    )
    covered_events: List[str] = Field(
        ..., description="Events covered under the policy"
    )
    deductible: float = Field(..., description="Deductible amount for the policy")
    total_coverage_amount: float = Field(
        ..., description="Total coverage amount of the policy"
    )


class CoverageInformation(BaseModel):
    coverage_type: str = Field(..., description="Type of coverage provided by the policy")
    coverage_events: List[str] = Field(..., description="Events covered under the policy")
    deductible: int = Field(..., description="Deductible amount for the policy")
    total_coverage_amount: int = Field(..., description="Total coverage amount of the policy")


class AdditionalInformation(BaseModel):
    no_claim_discount: str = Field(..., description="Discount applied for no claims")
    roadside_assistane: str = Field(..., description="Availability of roadside assistance")
    rental_reimbursement: str = Field(..., description="Reimbursement for rental expenses")


class VehicleInsuranceData(BaseModel):
    policyDetails: PolicyDetails
    coverageInformation: CoverageInformation
    vehicleInformation: VehicleInformation
    policyHolderInformation: PolicyHolderInformation
    additionalInformation: AdditionalInformation


class AllClaimantData:
    """Tool for retrieving claimant data."""

    def __init__(self):
        self.mock_db = None

    def mock_claimants(self):
        claimant_database = {
            "CLM-2024-44556": VehicleInsuranceData(
                policyDetails=PolicyDetails(
                    policy_holder_name="Ikenna Uzoh",
                    policy_start_date=datetime(2023, 1, 1),
                    policy_expiry_date=datetime(2029, 1, 1),
                    policy_status="Active",
                    coverage_type="Comprehensive",
                    covered_events=["Accident", "Theft", "Fire"],
                    deductible=500.0,
                    total_coverage_amount=10000.0,
                ),
                vehicleInformation=VehicleInformation(
                    vehicle_make="Toyota",
                    vehicle_model="Corolla",
                    year_of_manufacture=2023,
                    vin="1HGBH41JXMN109186",
                    license_plate_number="ABC-1234",
                ),
                policyHolderInformation=PolicyHolderInformation(
                    claimant_id="CLM-2024-44556",
                    name="Ikenna Uzoh",
                    contact="ikenna@masteryhive.ai",
                    address="123 Main St, Canada",
                    contact_number="+234-800-123-4567",
                    email="ikenna@masteryhive.ai",
                ),
                coverageInformation=CoverageInformation(
                    coverage_type="Comprehensive Motor Insurance",
                    coverage_events=["Accident", "Theft", "Fire"],
                    deductible=500.0,
                    total_coverage_amount=10000.0,
                ),
                additionalInformation=AdditionalInformation(
                    no_claim_discount="10%",
                    roadside_assistane="Included",
                    rental_reimbursement="Up to $30 per day for 10 days",
                ),
            ),
            "CLM-2024-24680": VehicleInsuranceData(
                policyDetails=PolicyDetails(
                    policy_holder_name="Tyrone Onyebuagu",
                    policy_start_date=datetime(2022, 6, 15),
                    policy_expiry_date=datetime(2029, 6, 15),
                    policy_status="Expired",
                    coverage_type="Third Party",
                    covered_events=["Accident"],
                    deductible=300.0,
                    total_coverage_amount=5000.0,
                ),
                vehicleInformation=VehicleInformation(
                    vehicle_make="Honda",
                    vehicle_model="Civic",
                    year_of_manufacture=2019,
                    vin="2HGBH41JXMN109187",
                    license_plate_number="DEF-5678",
                ),
                policyHolderInformation=PolicyHolderInformation(
                    claimant_id="CLM-2024-24680",
                    name="Tyrone Onyebuagu",
                    contact="tyrone@masteryhive.ai",
                    address="456 Elm St, Abuja",
                    contact_number="+234-800-234-5678",
                    email="tyrone@masteryhive.ai",
                ),
                coverageInformation=CoverageInformation(
                    coverage_type="Comprehensive Motor Insurance",
                    coverage_events=["Accident"],
                    deductible=300.0,
                    total_coverage_amount=5000.0,
                ),
                additionalInformation=AdditionalInformation(
                    no_claim_discount="5%",
                    roadside_assistane="Not Included",
                    rental_reimbursement="Not Available",
                ),
            ),
            "CLM-2024-43210": VehicleInsuranceData(
                policyDetails=PolicyDetails(
                    policy_holder_name="Franklin Elum",
                    policy_start_date=datetime(2021, 3, 10),
                    policy_expiry_date=datetime(2029, 3, 10),
                    policy_status="Expired",
                    coverage_type="Comprehensive",
                    covered_events=["Accident", "Theft"],
                    deductible=400.0,
                    total_coverage_amount=8000.0,
                ),
                vehicleInformation=VehicleInformation(
                    vehicle_make="Ford",
                    vehicle_model="Focus",
                    year_of_manufacture=2020,
                    vin="3HGBH41JXMN109188",
                    license_plate_number="GHI-9012",
                ),
                policyHolderInformation=PolicyHolderInformation(
                    claimant_id="CLM-2024-43210",
                    name="Franklin Elum",
                    contact="franklin@masteryhive.ai",
                    address="789 Pine St, Port Harcourt",
                    contact_number="+234-800-345-6789",
                    email="franklin@masteryhive.ai",
                ),
                coverageInformation=CoverageInformation(
                    coverage_type="Comprehensive Motor Insurance",
                    coverage_events=["Accident", "Theft"],
                    deductible=400.0,
                    total_coverage_amount=8000.0,
                ),
                additionalInformation=AdditionalInformation(
                    no_claim_discount="10%",
                    roadside_assistane="Included",
                    rental_reimbursement="Available",
                ),
            ),
        }
        return claimant_database


