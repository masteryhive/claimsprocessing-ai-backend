import json
from typing import Annotated
from langchain_core.tools import tool
from src.resources.retrieve_vehicle_policy import InsuranceDataExtractor
from src.resources.image_understanding import claims_image_evidence_recognizer
from src.config.appconfig import env_config


############## document extraction and completeness check ##############
@tool
def supporting_document_understanding(
    document_url: Annotated[str, "supporting document URL"],
):
    """
    Analyzes the document to determine what it is using the document URL.
    """
    return claims_image_evidence_recognizer(document_url)


@tool
def claims_document_completeness(policy_id: Annotated[str, "policy_id"]):
    """
    retrieve document completion status using policy_id
    """
    # Implement a logic to mock the different files
    res = f"""
    Claimant's policy ID: {policy_id}
    * The provided driver's license matches the name on the claim form.
    * The provided police report confirms the accident details.
    * The provided vehicle registration matches the vehicle on the claim form.
    ===
    {{"claims_document_completeness_status":"documents are complete!"}}
    """
    return res


############## Fraud checks tool ##############


@tool
def claimant_exists(
    policy_id: Annotated[str, "claimant's policy_id."],
    email: Annotated[str, "claimant's email."],
):
    """
    Verifies that the claimant is a real customer by checking the internal database using their policy_id and email.
    """
    # Implement the backend verification logic here
    return {
        "status": "success",
        "message": "Backend verification successful. Claimant is a valid customer",
    }


@tool
def policy_status_check(policy_id: Annotated[str, "claimant's policy_id."]):
    """
    checks if the status of the claimant's insurance policy is active using the policy_id
    """
    # Implement the policy status check logic here
    return {"status": "success", "message": f"Policy ID: {policy_id} is active!"}


@tool
def item_insurance_check(
    vehicle_registration_number: Annotated[
        str, "claimant's vehicle registration number."
    ]
):
    """
    calls the NIID database to see if the vehicle has been insured using the vehicle registration number.
    """
    try:
        extractor = InsuranceDataExtractor(vehicle_registration_number)
        try:
            # Call the method to perform the extraction
            data = extractor.extract_data()
        finally:
            # Ensure the driver is closed after extraction
            extractor.close_driver()
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        extractor.close_driver()


@tool
def item_pricing_check(
    damaged_part: Annotated[
        str, "from the picture evidence which parts are damaged."
    ]
):
    """
    calls the local market place to verify the quoted cost on the invoice.
    """
    #     "implement jiji search and cost extraction for docuement inflation"
    import requests
    from requests.auth import HTTPBasicAuth

    url = f"http://127.0.0.1:8000/api/v1/get-vehicle-policy?registration_number{vehicle_registration_number}"
    try:
        username = "sam@masteryhive.com"
        password = "JLg8m4aQ8n46nhC"
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


@tool
def calculate_fraud_risk(risk_factor: str):
    """
    Tool to calculate the fraud risk score
    """
    indicators = [0.75, 0.6, 0.85, 0.4, 0.7, 0.9]
    return int(risk_factor) * max(indicators)


############## claim summarizer ##############

# @tool
# def item_insurance_cost_check(input_data:str):
#     "implement jiji search and cost extraction for docuement inflation"


# @tool
# def risk_classification(input_data:str):
#     """
#     Classifies the risk level of the claim based on predefined criteria.
#     """
#     # Implement the risk classification logic here
#     return "Claim classified as low-risk."


# @tool
# def fraud_detection_tool(query: str) -> str:
#     """
#     This tool is used to detect potential fraud in insurance claims.
#     To use this tool, follow these guidelines:
#     - Provide the claim details in the query
#     - The tool will analyze the details for any signs of fraud
#     - It will return a report indicating the likelihood of fraud and any suspicious elements found

#     Use gemini multi-modal to implement invoice document figure extraction.
#     """
#     # Simulate fraud detection logic
#     claim_data = json.loads(query)
#     suspicious_elements = []

#     # Example checks (these would be more complex in a real scenario)
#     if claim_data.get("amount", 0) > 10000:
#         suspicious_elements.append("High claim amount")
#     if claim_data.get("status") == "Pending" and claim_data.get("type") == "Theft":
#         suspicious_elements.append("Pending theft claim")

#     if suspicious_elements:
#         return json.dumps({
#             "fraud_status": "suspicious",
#             "details": suspicious_elements
#         })
#     else:
#         return json.dumps({
#             "fraud_status": "clear",
#             "details": "No suspicious elements detected"
#         })
