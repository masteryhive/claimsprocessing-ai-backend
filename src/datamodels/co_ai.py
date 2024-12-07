from pydantic import BaseModel, Field

# Data model for input validation
class MessageRequest(BaseModel):
    message: str

class ProcessClaimTask(BaseModel):
    claim_id: int
    task_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": 56,
                "task_id": "TASK123_12:08:34"
            }
        }

class AIClaimsReport(BaseModel):
    claimId: int = Field(..., description="The unique identifier for the claim.")
    fraudScore: float = Field(default=0.0, description="The calculated fraud score as a percentage.")
    fraudIndicators: list = Field(default=[], description="A list of indicators suggesting potential fraud.")
    aiRecommendation: list = Field(default=[], description="A list of AI-generated recommendations for claim processing.")
    policyReview: list = Field(default=[], description="A list of policy review items related to the claim.")
    evidenceProvided: list = Field(default=[], description="A list of evidence items provided for the claim.")
    coverageStatus: str = Field(default="", description="The status of the coverage for the claim.")
    typeOfIncident: str = Field(default="", description="The type of incident related to the claim.")
    details: str = Field(default="", description="Detailed information about the claim.")
    discoveries: list = Field(default=[], description="A list of discoveries made during the claim investigation.")

class UpdateClaimsReportModel(BaseModel):
    fraudScore: float = Field(default=0.0, description="The calculated fraud score as a percentage.")
    fraudIndicators: list = Field(default=[], description="A list of indicators suggesting potential fraud.")
    aiRecommendation: list = Field(default=[], description="A list of AI-generated recommendations for claim processing.")
    policyReview: list = Field(default=[], description="A list of policy review items related to the claim.")
    evidenceProvided: list = Field(default=[], description="A list of evidence items provided for the claim.")
    coverageStatus: str = Field(default="", description="The status of the coverage for the claim.")
    typeOfIncident: str = Field(default="", description="The type of incident related to the claim.")
    details: str = Field(default="", description="Detailed information about the claim.")
    discoveries: list = Field(default=[], description="A list of discoveries made during the claim investigation.")