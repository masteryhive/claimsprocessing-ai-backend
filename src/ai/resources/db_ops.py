import json
from typing import Union

import requests
from src.error_trace.errorlogger import log_error
from src.datamodels.claim_processing import CreateClaimsReport, UpdateClaimsReportModel
from src.config.appconfig import env_config

async def save_claim_database(data_to_send: dict) -> bool:
        """
        This tool saves claims information to the database by sending a POST request to the backend API.
        
        Parameters:
        - data_tO_send: dictionary
        Returns:
        - A string message indicating the success or failure of the operation.
        """
        import requests
        # Send a POST request to the endpoint
        response = requests.post(env_config.backend_api+"/claims", json=data_to_send)

        # Check if the request was successful
        if response.status_code == 201:
            return True
        else:
            log_error(f"Failed to send claim details: {response.status_code} - {response.text}")
            return f"Failed to send claim details: {response.status_code} - {response.text}"

def get_claim_from_database(claim_request:dict) -> dict:
        import requests
        # Send a POST request to the endpoint
        response = requests.get(env_config.backend_api+f"/claims/{claim_request['claim_id']}")

        # Check if the request was successful
        if response.status_code == 200:
            resp_data = response.json()
            return resp_data
        else:
            return f"Failed to get claim details: {response.status_code} - {response.text}"

def update_claim_status_database(claim_id: int, status:str) -> Union[str,bool]:
    """
    This function updates the status of a claim in the database by sending a PATCH request to the backend API.

    Parameters:
    - claim_id: integer representing the unique identifier of the claim
    - status: string representing the new status to be set for the claim
    Returns:
    - A string message indicating the success or failure of the operation.
    """
    try:
        import requests

        # Send a POST request to the endpoint
        response = requests.patch(env_config.backend_api+f"/claims/{claim_id}", json={"status":status})
        # Check if the request was successful
        if response.status_code == 200:
            return True
        else:
            log_error(f"Failed to send claim details: {response.status_code} - {response.text}")
            return f"Failed to send claim details: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred while updating the claim: {str(e)}"



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
        print(json.dumps(model_result))
        # Send a POST request to the endpoint
        response = requests.post(env_config.backend_api + "/claim-report", json=model_result)
        
        # Check if the request was successful
        if response.status_code == 201:
            return True
        else:
            print(f"Failed to send claim details: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

def update_claim_report_database(claim_id:int,claim_report: dict) -> bool:
    """
    This function saves claims report information to the database by sending a POST request to the backend API.
    
    Parameters:
    - claim_report: dictionary
    Returns:
    - A boolean indicating whether the operation was successful.
    """
    try:
        # Assuming CreateClaimsReport is a class that takes a dictionary and converts it to a model instance
        model_instance = UpdateClaimsReportModel(**claim_report)  # Instantiate the model
        
        # Convert model instance to a dictionary or JSON-serializable format
        model_result = model_instance.model_dump()  # or json.dumps(model_instance) if it's a dict-like object
        print(json.dumps(model_result))
        # Send a POST request to the endpoint
        response = requests.patch(env_config.backend_api + f"/claim-report/by-claim/{claim_id}", json=model_result)
        
        # Check if the request was successful
        if response.status_code == 200:
            return True
        else:
            print(f"Failed to send claim details: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error occurred: {e}")
        return False