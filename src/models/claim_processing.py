from pydantic import BaseModel, Field
from typing import Any, List, Optional, Dict, Union
from datetime import datetime


class ProcessClaimTask(BaseModel):
    claim_id: int
    task_id: str
    tenant_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": 56,
                "task_id": "TASK123_12:08:34",
                "tenant_id": "tenant_123"
            }
        }

class AccidentClaimData(BaseModel):
    nameOfInsured: str
    policyNumber: str
    addressOfInsured: str
    phoneNumberOfInsured: str
    declaration: bool
    extentOfLossOrDamage: List[Union[dict,str]]
    personInCharge: str
    addressOfPersonInCharge: str
    permissionConfirmation: str
    otherInsuranceConfirmation: str
    purposeOfUse: str
    durationOfOwnership: str
    incidentDetails: str
    previousOwner: str
    servicedBy: str
    lastServiceDate: str
    totalMileage: str
    vehicleMake: str
    vehicleModel: Optional[str] = Field(default="")
    claimType: str
    registrationNumber: str
    claimantName: str
    vehicleColor: str
    typeOfBody: str
    yearOfManufacture: str
    chassisNumber: str
    engineNumber: str
    dateOfDiscovery: Union[str,None]
    vehicleLicenseNumber: str
    policeStationName: str
    evidenceProvided: List[Any]
    ssim: dict
    dateClaimFiled: str
    repairInvoice:str

class TheftClaimData(BaseModel):
    id: int
    nameOfInsured: str
    policyNumber: str
    addressOfInsured: str
    phoneNumberOfInsured: str
    declaration: bool
    signature: str
    status: str
    signatureDate: str
    extentOfLossOrDamage: List[Union[dict,str]]
    particularsAddress: str
    particularsPhoneNo: str
    personInCharge: str
    addressOfPersonInCharge: str
    permissionConfirmation: str
    otherInsuranceConfirmation: str
    purposeOfUse: str
    durationOfOwnership: str
    incidentDetails: str
    previousOwner: str
    servicedBy: str
    lastServiceDate: str
    totalMileage: str
    vehicleMake: str
    vehicleModel: Optional[str] = Field(default="")
    claimType: str
    registrationNumber: str
    claimantName: str
    vehicleCC: str
    vehicleColor: str
    typeOfBody: str
    yearOfManufacture: str
    chassisNumber: str
    engineNumber: str
    locationAtTimeOfTheft: str
    dateOfDiscovery: Union[str,None]
    discoveredBy: str
    howTheftOccurred: str
    vehicleLicenseNumber: str
    dateReported: Union[str,None]
    policeStationName: str
    wasVehicleLocked: str
    wasNightWatchmanInAttendance: str
    suspect: str
    suspectDetails: str
    roomId: str
    evidenceProvided: List[Any]
    dateClaimFiled: str


class CreateClaimsReport(BaseModel):
    claimId: int = Field(..., description="The unique identifier for the claim.")
    fraudScore: float = Field(default=0.0, description="The calculated fraud score as a percentage.")
    fraudIndicators: list = Field(default=[], description="A list of indicators suggesting potential fraud.")
    aiRecommendation: list = Field(default=[], description="A list of AI-generated recommendations for claim processing.")
    policyReview: str = Field(default="", description="A list of policy review items related to the claim.")
    evidenceProvided: list = Field(default=[], description="A list of evidence items provided for the claim.")
    coverageStatus: str = Field(default="", description="The status of the coverage for the claim.")
    typeOfIncident: str = Field(default="", description="The type of incident related to the claim.")
    details: str = Field(default="", description="Detailed information about the claim.")
    discoveries: list = Field(default=[], description="A list of discoveries made during the claim investigation.")

class UpdateClaimsReportModel(BaseModel):
    fraudScore: float = Field(default=0.0, description="The calculated fraud score as a percentage.")
    fraudIndicators: list = Field(default=[], description="A list of indicators suggesting potential fraud.")
    aiRecommendation: list = Field(default=[], description="A list of AI-generated recommendations for claim processing.")
    policyReview: str = Field(default="", description="A list of policy review items related to the claim.")
    evidenceProvided: list = Field(default=[], description="A list of evidence items provided for the claim.")
    coverageStatus: str = Field(default="", description="The status of the coverage for the claim.")
    typeOfIncident: str = Field(default="", description="The type of incident related to the claim.")
    details: str = Field(default="", description="Detailed information about the claim.")
    discoveries: list = Field(default=[], description="A list of discoveries made during the claim investigation.")
    settlementOffer: str = Field(default="", description="The settlement offer details for the claim.")
    preLossComparison: str = Field(default="", description="Comparison details of the vehicle's condition before the loss.")