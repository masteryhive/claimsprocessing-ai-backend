from typing import Annotated
from langchain_core.tools import tool

@tool
def policy_validity(policy_number: Annotated[str, "policy_number"]):
    """
    verify that the policy has not expired using policy_id
    """
    # Implement RAG on policy document here

    return {"status":"policy is still active and valid!"}