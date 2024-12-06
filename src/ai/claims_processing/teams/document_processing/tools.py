
############## document extraction and completeness check ##############
from typing import Annotated
from src.ai.resources.document_understanding import document_understanding
from src.ai.resources.image_understanding import claims_image_evidence_recognizer
from langchain_core.tools import tool

@tool
def verify_claim_supporting_documents_in_image_format(
    resource_url: Annotated[str, "URL of the supporting evidence(resourceUrls) in image format to be reviewed (e.g https://storage.googleapis.com/masteryhive-insurance-claims/f1b2f49b-6fe8-453e-bdb4-7e22b166c092/supporting_documents/download.jpeg)"],
):
    """
    use this tool for images ONLY. This tool reviews the provided supporting documents in image formats and extracts key details to verify the claim.
    It processes the document from the provided URL and performs necessary validation and extraction.
    """
    return claims_image_evidence_recognizer(resource_url)

@tool
def verify_claim_supporting_documents_in_pdf(
    resource_url: Annotated[str, "URL of the supporting evidence(resourceUrls) in pdf format to be reviewed (e.g https://storage.googleapis.com/masteryhive-insurance-claims/rawtest/Scenario2/Auto_shop_invoice.pdf)"],
):
    """
    This tool reviews the provided supporting documents in pdf format and extracts key details to verify the claim.
    It processes the document from the provided URL and performs necessary validation and extraction.
    """
    resp = document_understanding(resource_url)
    return resp



