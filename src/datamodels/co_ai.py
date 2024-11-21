from pydantic import BaseModel

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