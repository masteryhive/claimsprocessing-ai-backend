
############## document extraction and completeness check ##############
from typing import Annotated
from src.ai.resources.image_understanding import claims_image_evidence_recognizer
from langchain_core.tools import tool

@tool
def review_supporting_documents(
    evidence_url: Annotated[str, "URL to the supporting document"],
):
    """
    Use this tool to review supporting evidence/documents and extract relevant information.
    """
    return claims_image_evidence_recognizer(evidence_url)





