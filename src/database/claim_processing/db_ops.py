import json
from typing import Union

import httpx
from src.database.schemas import ClaimsReport
import requests
from src.error_trace.errorlogger import log_error
from src.datamodels.claim_processing import CreateClaimsReport, UpdateClaimsReportModel
from src.config.appconfig import env_config
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

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
        # Send a PATCH request to the endpoint using httpx
        with httpx.Client() as client:
            response = client.patch(env_config.backend_api + f"/claim-report/by-claim/{claim_id}", json=model_result)
        
        # Check if the request was successful
        if response.status_code == 200:
            return True
        else:
            print(f"Failed to send claim details: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error occurred: {e}")
        return False
    


def create_claim_report(
    db: Session,
    id: str,
    fraud_score: float,
    fraud_indicators: list,
    discoveries: list,
    ai_recommendation: list,
    policy_review: str,
    evidence_provided: list,
    coverage_status: str,
    type_of_incident: str,
    details: str,
):
    """
    Create a new claim record
    """
    claim_report = ClaimsReport(
        id=id,
        fraud_score=fraud_score,
        discoveries=discoveries,
        fraud_indicators=fraud_indicators,
        ai_recommendation=ai_recommendation,
        policy_review=policy_review,
        evidence_provided=evidence_provided,
        coverage_status=coverage_status,
        details=details,
        type_of_incident=type_of_incident,
    )
    db.add(claim_report)
    db.commit()
    db.refresh(claim_report)
    db.close()

def delete_claim_report_by_id(db: Session, claim_id: int) -> bool:
    """
    Delete a claim report by its ID.

    Parameters:
    - db: Database session
    - claim_id: ID of the claim report to be deleted

    Returns:
    - A boolean indicating whether the deletion was successful.
    """
    try:
        # Query the claim report by ID
        claim_report = db.query(ClaimsReport).filter(ClaimsReport.id == claim_id).first()
        
        if not claim_report:
            logger.error(f"Claim report with ID {claim_id} not found.")
            return False

        # Delete the claim report
        db.delete(claim_report)
        db.commit()
        logger.info(f"Claim report with ID {claim_id} successfully deleted.")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting claim report with ID {claim_id}: {str(e)}")
        return False
