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
            return f"Failed to send claim details: {response.status_code} - {response.text}"

def get_claim_from_database(policy:dict) -> dict:
        import requests
        # Send a POST request to the endpoint
        response = requests.get(env_config.backend_api+f"/claims/policy/{policy['policy_number']}")

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            return f"Failed to send claim details: {response.status_code} - {response.text}"

async def update_claim_database(claim_id: str, resource_url:list) -> str:
        """
        This tool saves claims information to the database by sending a POST request to the backend API.
        
        Parameters:
        - data_to_send: dictionary
        Returns:
        - A string message indicating the success or failure of the operation.
        """
        try:
            import requests

            # Send a POST request to the endpoint
            response = requests.patch(env_config.backend_api+f"/claims/{claim_id}", json={"resourceUrls":resource_url})
            # Check if the request was successful
            if response.status_code == 200:
                return True
            else:
                return f"Failed to send claim details: {response.status_code} - {response.text}"
        except Exception as e:
            return f"An error occurred while updating the claim: {str(e)}"
        
def save_claim_report_database(claim_report: dict) -> bool:
        """
        This function aves claims report information to the database by sending a POST request to the backend API.
        
        Parameters:
        - claim_report: dictionary
        Returns:
        - A string message indicating the success or failure of the operation.
        """
        import requests
        # Send a POST request to the endpoint
        response = requests.post(env_config.backend_api+"/claim-report", json=claim_report)
        # Check if the request was successful
        if response.status_code == 201:
            return True
        else:
            return f"Failed to send claim details: {response.status_code} - {response.text}"