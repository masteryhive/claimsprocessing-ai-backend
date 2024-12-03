
############## document extraction and completeness check ##############
from typing import Annotated
from src.ai.resources.image_understanding import claims_image_evidence_recognizer
from langchain_core.tools import tool

@tool
def supporting_document_understanding(
    document_url: Annotated[str, "supporting document URL"],
):
    """
    Analyzes the document to determine what it is using the document URL.
    """
    return claims_image_evidence_recognizer(document_url)


@tool
def claims_document_completeness(policy_number: Annotated[str, "policy_number"]):
    """
    retrieve document completion status using policy_id
    """
    # Implement a logic to mock the different files
    res = f"""
    Claimant's policy ID: {policy_number}
    * The provided driver's license matches the name on the claim form.
    * The provided police report confirms the accident details.
    * The provided vehicle registration matches the vehicle on the claim form.
    ===
    {{"status":"documents are complete!"}}
    """
    return res

