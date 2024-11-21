import json
from typing import Annotated
from langchain_core.tools import tool
from config.appconfig import env_config


############## document extraction and completeness check ##############
@tool
def claims_document_understanding(
    prompt: Annotated[str, "what you need to know about the document"],
    document_url: Annotated[str, "document URL"],
):
    """
    Analyzes the document to determine what it is by providing a prompt and the document URL.
    """
    return ""


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
    import requests
    from requests.auth import HTTPBasicAuth

    url = f"http://127.0.0.1:8000/api/v1/get-vehicle-policy?registration_number{vehicle_registration_number}"
    try:
        username = "mahengr"
        password = "admin0000#"
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"


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
@tool
def save_claim_report_database(
    vehicle_registration_number: Annotated[
        str, "claimant's vehicle registration number."
    ],
    fraud_indicators: Annotated[list, "List of indicators suggesting potential fraud."],
    recommmendations: Annotated[
        list, "List of recommendations based on the claim analysis."
    ],
    policy_review: Annotated[str, "Summary of the policy review findings."],
    fraud_score: Annotated[str, "Calculated fraud risk score."],
    evidence_provided: Annotated[list, "List of evidence provided for the claim."],
    type_of_inciddent: Annotated[str, "Type of incident related to the claim."],
    details: Annotated[str, "Detailed description of the claim."],
    coverage_status: Annotated[str, "Status of the insurance coverage for the claim."],
    claim_id: Annotated[str, "Unique identifier for the claim."],
) -> str:
    """
    This tool saves claims information to the database by sending a POST request to the backend API.

    Parameters:
    - data_to_send: dictionary
    Returns:
    - A string message indicating the success or failure of the operation.
    """
    import requests

    data_to_send = {
        "vehicle_registration_number": vehicle_registration_number,
        "fraud_indicators": fraud_indicators,
        "ai_recommendation": recommmendations,
        "policy_review": policy_review,
        "fraud_score": float(fraud_score),
        "evidence_provided": evidence_provided,
        "type_of_incident": type_of_inciddent,
        "details": details,
        "coverage_status": coverage_status,
        "claim_id": claim_id,
    }

    # Send a POST request to the endpoint
    response = requests.post(
        env_config.backend_api + f"/claims-report", json=data_to_send
    )

    # Check if the request was successful
    if response.status_code == 201:
        print(response.json())
        return "Claim details successfully inserted to database."
    else:
        return f"Failed to send claim details: {response.status_code} - {response.text}"


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
