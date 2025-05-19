import json
from typing import Union
import httpx,requests
from src.error_trace.errorlogger import system_logger
from src.models.claim_processing import CreateClaimsReport, UpdateClaimsReportModel
from src.config.appconfig import env_config
from sqlalchemy.orm import Session



def get_claim_from_database(claim_id:str, x_tenant_id: str = None) -> dict:
        try:
            # Send a POST request to the endpoint
            headers = {"x_tenant_id": x_tenant_id} if x_tenant_id else {}
            response = requests.get(env_config.backend_api+f"/claims/{claim_id}", headers=headers)

            # Check if the request was successful
            if response.status_code == 200:
                resp_data = response.json()
                return resp_data
            else:
                return f"Failed to get claim details: {response.status_code} - {response.text}"
        except Exception as e:
            system_logger.error(error=f"An error occurred while fetching claim details: {str(e)}")

def update_claim_status_database(claim_id: int, status:str, x_tenant_id: str = None) -> Union[str,bool]:
    """
    This function updates the status of a claim in the database by sending a PATCH request to the backend API.

    Parameters:
    - claim_id: integer representing the unique identifier of the claim
    - status: string representing the new status to be set for the claim
    - x_tenant_id: string representing the tenant identifier
    Returns:
    - A string message indicating the success or failure of the operation.
    """
    try:
        # Send a POST request to the endpoint
        headers = {"x_tenant_id": x_tenant_id} if x_tenant_id else {}
        response = requests.patch(env_config.backend_api+f"/claims/{claim_id}", json={"status":status}, headers=headers)
        # Check if the request was successful
        if response.status_code == 200:
            return True
        else:
            system_logger.error(error=f"Failed to update claim status into database: {response.status_code} - {response.text}")
            return f"Failed to send claim details: {response.status_code} - {response.text}"
    except Exception as e:
        system_logger.error(error=f"An error occurred while updating the claim: {str(e)}")



def save_claim_report_database(claim_report: dict, x_tenant_id: str = None) -> bool:
    """
    This function saves claims report information to the database by sending a POST request to the backend API.
    
    Parameters:
    - claim_report: dictionary
    - x_tenant_id: string representing the tenant identifier
    Returns:
    - A boolean indicating whether the operation was successful.
    """
    try:
        # Assuming CreateClaimsReport is a class that takes a dictionary and converts it to a model instance
        model_instance = CreateClaimsReport(**claim_report)  # Instantiate the model
        
        # Convert model instance to a dictionary or JSON-serializable format
        model_result = model_instance.model_dump()  # or json.dumps(model_instance) if it's a dict-like object
        print(json.dumps(model_result))
        # Send a POST request to the endpoint
        headers = {"x_tenant_id": x_tenant_id} if x_tenant_id else {}
        response = requests.post(env_config.backend_api + "/claim-report", json=model_result, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 201:
            return True
        else:
            system_logger.error(error=f"Failed to save claim status into database: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        system_logger.error(error=f"Error occurred while saving claim report to database: {e}")
        return False

def update_claim_report_database(claim_id:int, claim_report: UpdateClaimsReportModel, x_tenant_id: str = None) -> bool:
    """
    This function saves claims report information to the database by sending a POST request to the backend API.
    
    Parameters:
    - claim_report: dictionary
    - x_tenant_id: string representing the tenant identifier
    Returns:
    - A boolean indicating whether the operation was successful.
    """
    try:
        # Convert model instance to a dictionary or JSON-serializable format
        model_result = claim_report.model_dump()
        print(json.dumps(model_result))
        # Send a PATCH request to the endpoint using httpx
        headers = {"x_tenant_id": x_tenant_id} if x_tenant_id else {}
        with httpx.Client() as client:
            response = client.patch(env_config.backend_api + f"/claim-report/by-claim/{claim_id}", json=model_result, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            return True
        else:
            system_logger.error(error=f"Failed to update claim report into database: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        system_logger.error(error=f"An error occurred while updating the claim report: {str(e)}")
    