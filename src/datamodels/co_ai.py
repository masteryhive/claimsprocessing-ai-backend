from pydantic import BaseModel, Field

# Data model for input validation
class MessageRequest(BaseModel):
    message: str

class ProcessClaimTask(BaseModel):
    policy_number: str
    task_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "policy_number": "POLICY456",
                "task_id": "TASK123_12:08:34"
            }
        }

class AIClaimsReport(BaseModel):
    fraud_score: float = Field(..., description="The calculated fraud score as a percentage.")
    fraud_indicators: list = Field(..., description="A list of indicators suggesting potential fraud.")
    ai_recommendation: list = Field(..., description="A list of AI-generated recommendations for claim processing.")
    policy_review: list = Field(..., description="A list of policy review items related to the claim.")
    class Config:
        json_schema_extra = {
            "example": {
                "fraud_score": 85.0,
                "fraud_indicators": ["High claim amount", "Inconsistent statements"],
                "ai_recommendation": ["Approve claim", "Verify police report"],
                "policy_review": ["Coverage Status: Active", "Terms: Theft covered"]
            }
        }