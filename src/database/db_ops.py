import json
from typing import Union
import requests
from src.error_trace.errorlogger import system_logger
from src.models.claim_processing import CreateClaimsReport, UpdateClaimsReportModel
from src.config.appconfig import env_config
from sqlalchemy.orm import Session
import pybreaker

# Circuit breaker configuration
circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=5,  # Number of failures before opening the circuit
    reset_timeout=60  # Time to wait before trying again
)

def get_claim_from_database(claim_id: str) -> dict:
    try:
        # Send a GET request to the endpoint
        response = requests.get(env_config.backend_api + f"/claims/{claim_id}")

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 500:
            system_logger.error(f"Server error (500) while fetching claim details for ID {claim_id}: {response.text}")
            raise Exception("Internal Server Error")
        else:
            system_logger.error(f"Failed to get claim details: {response.status_code} - {response.text}")
            return {"error": f"Failed to get claim details: {response.status_code} - {response.text}"}
    except Exception as e:
        system_logger.error(f"An error occurred while fetching claim details: {str(e)}")
        return {"error": str(e)}

@circuit_breaker
def update_claim_status_database(claim_id: int, status: str) -> Union[str, bool]:
    """
    This function updates the status of a claim in the database by sending a PATCH request to the backend API.

    Parameters:
    - claim_id: integer representing the unique identifier of the claim
    - status: string representing the new status to be set for the claim

    Returns:
    - A string message indicating the success or failure of the operation.
    """
    try:
        # Send a PATCH request to the endpoint
        response = requests.patch(env_config.backend_api + f"/claims/{claim_id}", json={"status": status})

        # Check if the request was successful
        if response.status_code == 200:
            return True
        elif response.status_code == 500:
            system_logger.error(f"Server error (500) while updating claim status for ID {claim_id}: {response.text}")
            raise Exception("Internal Server Error")
        else:
            system_logger.error(f"Failed to update claim status: {response.status_code} - {response.text}")
            return f"Failed to send claim details: {response.status_code} - {response.text}"
    except Exception as e:
        system_logger.error(f"An error occurred while updating claim status: {str(e)}")
        return False

def save_claim_report_database(claim_report: dict) -> bool:
    """
    This function saves claims report information to the database by sending a POST request to the backend API.

    Parameters:
    - claim_report: dictionary

    Returns:
    - A boolean indicating whether the operation was successful.
    """
    try:
        # Assuming CreateClaimsReport is a class that takes a dictionary and converts it to a model instance
        model_instance = CreateClaimsReport(**claim_report)  # Instantiate the model

        # Convert model instance to a dictionary or JSON-serializable format
        model_result = model_instance.model_dump()  # or json.dumps(model_instance) if it's a dict-like object

        # Send a POST request to the endpoint
        response = requests.post(env_config.backend_api + "/claim-report", json=model_result)

        # Check if the request was successful
        if response.status_code == 201:
            return True
        elif response.status_code == 500:
            system_logger.error(f"Server error (500) while saving claim report: {response.text}")
            raise Exception("Internal Server Error")
        else:
            system_logger.error(f"Failed to save claim report: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        system_logger.error(f"Error occurred while saving claim report to database: {str(e)}")
        return False

def update_claim_report_database(claim_id: int, claim_report: UpdateClaimsReportModel) -> bool:
    """
    This function updates claims report information in the database by sending a PATCH request to the backend API.

    Parameters:
    - claim_id: integer representing the unique identifier of the claim
    - claim_report: UpdateClaimsReportModel instance

    Returns:
    - A boolean indicating whether the operation was successful.
    """
    try:
        # Convert model instance to a dictionary or JSON-serializable format
        model_result = claim_report.model_dump()

        # Send a PATCH request to the endpoint using requests
        response = requests.patch(env_config.backend_api + f"/claim-report/by-claim/{claim_id}", json=model_result)

        # Check if the request was successful
        if response.status_code == 200:
            return True
        elif response.status_code == 500:
            system_logger.error(f"Server error (500) while updating claim report for ID {claim_id}: {response.text}")
            raise Exception("Internal Server Error")
        else:
            system_logger.error(f"Failed to update claim report: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        system_logger.error(f"An error occurred while updating the claim report: {str(e)}")
        return False
