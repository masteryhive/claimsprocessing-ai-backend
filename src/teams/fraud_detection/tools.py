
import os
from pathlib import Path
from langchain_core.tools import tool
from typing import Annotated, Any, Dict, List, Union
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from src.teams.resources.image_understanding import SSIM
from src.rag.context_stuffing import process_query
from src.teams.resources.cost_benchmarking import CostBenchmarkingPlaywright
from src.teams.resources.retrieve_vehicle_policy import InsuranceDataExtractor


############## Fraud checks tool ##############
rag_path = Path(__file__).parent.parent / "policy_doc/"

@tool
def verify_this_claimant_exists_as_a_customer(
    policy_number: Annotated[str, "claimant's policy number."],
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
def investigate_if_this_claimant_is_attempting_a_rapid_policy_claim(date_claim_filed: Annotated[str, "date this claim was filed"],
                                                                    policy_number: Annotated[str, "the claimant's policy number"]):
    """
    Use this tool to check for rapid policy claims; to verify the claimant is not making a claim right after creating an insuring this vehicle.
    Args:
        policy_number (str): The claimant's policy number.
        date_claim_filed: (str): The date this claim was filed.
    """
    # Retrieve
    query = f"this claim is/was filed: {date_claim_filed}.\nRespond with only the date the policy start in this format November 16, 2024, and do nothing else. interprete the insurance period as DD/MM/YYYY."
    resp = process_query(query=query,pdf_path=f"{rag_path}/{policy_number.replace("/", "-")}.pdf")
  
    from datetime import datetime
    def calc(date_claim_filed,resp):
        # Extract the date from the response
        start_date_str = resp.split("<answer>")[1].split("</answer>")[0].strip()
        date_claim_filed_dt = None
        # Convert the dates from string to datetime objects
        try:
            date_claim_filed_dt = datetime.strptime(date_claim_filed, "%B %d %Y")
        except Exception as e:
            try:
                date_claim_filed_dt = datetime.strptime(date_claim_filed, "%B %d, %Y")
            except Exception as e:
                # Use today's date if parsing fails
                date_claim_filed_dt = datetime.today()

        start_date_dt = datetime.strptime(start_date_str, "%B %d, %Y")

        # Calculate the difference in days
        days_difference = (date_claim_filed_dt - start_date_dt).days

        # Determine if the claim was filed three days after the start of the insurance period
        if days_difference == 3:
            return "Yes, the claim was filed three days after the start of the insurance period."
        else:
            return "No, the claim was not filed three days after the start of the insurance period."
    return calc(date_claim_filed,resp)


############## vehicle fraud ##################
niid_data = {}
class SSIMInput(BaseModel):
    prelossUrl: str = Field(description="The URL of the pre-loss condition image.")
    claimUrl: str = Field(description="The URL of the claim condition image of the vehicle.")
    claimant_incident_detail: str = Field(description='A description of the incident that happened to the user, e.g., "A reckless driver hit my car from behind and broke my rear lights."')


def verify_vehicle_matches_preloss_using_SSIM_func(prelossUrl: str, claimUrl: str, claimant_incident_detail: str) -> str:
    """
    Use this tool to verify if the damages in the claim being filed for this vehicle matches its pre-loss condition using Structural Similarity Index (SSIM).
    
    Args:
    prelossUrl (str): The URL of the pre-loss condition image.
    claimUrl (str): The URL of the claim condition image.
    claimant_incident_detail (str): A description of the incident that happened to the user.
    
    Returns:
    str: The result of the SSIM analysis.
    """
    try:
        ssim_data = [
            {
            "prelossUrl":prelossUrl,
            "claimUrl": claimUrl
        }
        ]

        resp = SSIM(claimant_incident_detail,ssim_data)
        return resp
    except Exception as e:
        return {"status": "error", "message": str(e)}

verify_vehicle_matches_preloss_using_SSIM = StructuredTool.from_function(
    func=verify_vehicle_matches_preloss_using_SSIM_func,
    name="Verify Vehicle Matches Preloss using SSIM",
    description="verify if vehicle matches preloss using structured similarity index",
    args_schema=SSIMInput,
    return_direct=True,
)

@tool
def validate_if_this_is_a_real_vehicle(vehicle_information: Annotated[str, "vehicle make and brand. e.g toyota corolla 2012"]):
    """
    Check if the provided vehicle information corresponds to a real vehicle to mitigate ghost vehicle claims.
    """
    # Simulate a check for ghost claims
    return {"status": "clear", "message": "This vehicle is valid."}


@tool
def check_NIID_database_to_confirm_vehicle_insurance(
    vehicle_registration_number: Annotated[
        str, "claimant's vehicle registration number."
    ]
):
    """
    calls the NIID database to see if the vehicle has been insured using the vehicle registration number.
    """
    global niid_data

    extractor = InsuranceDataExtractor(vehicle_registration_number)
    niid_data = extractor.run()
    if niid_data.get('status') == 'success':
        niid_data["insured_message"] = "Yes, this vehicle is insured by NIID"
    else:
        niid_data["insured_message"] = "No, this vehicle is not insured by NIID"
    return niid_data["insured_message"]


@tool
def vehicle_chasis_number_matches_NIID_records(vehicle_chasis_number: Annotated[str, "the chasisNumber"]):
    """
    Verify vehicle chasis matches NIID internal database records.
    """
    # Simulate a registration match check
    if niid_data.get('status') == 'success' and niid_data.get('data')["ChassisNumber"] == vehicle_chasis_number:
        niid_data["message"] = "Yes, this vehicle chasis number matches NIID internal database records"
    else:
        niid_data["message"] = "No, this vehicle chasis number does not match NIID internal database records"
    return niid_data["message"]

############## damage cost fraud ##################

# Create a singleton instance at module level
_benchmarking_instance = None

def get_benchmarking_instance():
    global _benchmarking_instance
    if _benchmarking_instance is None:
        email = "sam@masteryhive.ai"
        password = "JLg8m4aQ8n46nhC"
        _benchmarking_instance = CostBenchmarkingPlaywright(email, password)
    return _benchmarking_instance

@tool
def item_cost_price_benchmarking_in_local_market(
    vehicle_name_and_model_and_damaged_part: Annotated[str, "search term"],
    quoted_cost: Annotated[str, "quoted cost"]
) -> str:
    """
    Benchmarks the quoted cost for vehicle repairs against local market prices.
    """
    benchmarking = get_benchmarking_instance()
    
    try:
        global market_prices
        tokunbo_prices = benchmarking.fetch_market_data(f"{vehicle_name_and_model_and_damaged_part} tokunbo")
        brand_new_prices = benchmarking.fetch_market_data(f"{vehicle_name_and_model_and_damaged_part} brand new")
        
        market_prices = {
            "tokunbo": tokunbo_prices,
            "brand_new": brand_new_prices
        }
        
        if tokunbo_prices and brand_new_prices:
            quoted_cost_value = float(quoted_cost.replace("\u20a6", "").replace(",", ""))
            tokunbo_analysis = benchmarking.analyze_price(tokunbo_prices, quoted_cost_value)
            brand_new_analysis = benchmarking.analyze_price(brand_new_prices, quoted_cost_value)
            print(f"FAIRLY USED (Tokunbo):\n{tokunbo_analysis}\n\nBRAND NEW:\n{brand_new_analysis}")
            return f"FAIRLY USED (Tokunbo):\n{tokunbo_analysis}\n\nBRAND NEW:\n{brand_new_analysis}"
        return "Unable to fetch market prices. Please try again later."
    except Exception as e:
        print(f"Error in benchmarking: {e}")
        return "An error occurred while benchmarking the cost. Please try again later."

@tool
def item_pricing_evaluator(
    vehicle_name_and_model_and_damaged_part: Annotated[str, "search term"]
):
    """
     this cost evaluation tool checks the local market place for how much the damaged part is worth.
    """
    benchmarking = get_benchmarking_instance()
    print("ok")
    try:
        if market_prices:
            tokunbo_analysis = benchmarking.run_with_expected_range(
                vehicle_name_and_model_and_damaged_part,
                market_prices["tokunbo"]
            )
            brand_new_analysis = benchmarking.run_with_expected_range(
                vehicle_name_and_model_and_damaged_part,
                market_prices["brand_new"]
            )
            return f"FAIRLY USED (Tokunbo):\n{tokunbo_analysis}\n\nBRAND NEW:\n{brand_new_analysis}"
        return "Unable to fetch market prices. Please try again later."
    except Exception as e:
        return "sorry, this tool can not be used at the moment"
    

################### other checks ################
@tool
def claimant_location_check(claimant_id: str, location: str):
    """
    Check claimant's location.
    """
    # Simulate a location check
    if location == "UNKNOWN":
        return {"status": "suspicious", "message": "Claimant location is unknown."}
    return {"status": "clear", "message": "Claimant location verified."}

@tool
def weather_traffic_conditions_check(date: str, location: str):
    """
    Check weather and traffic conditions.
    """
    # Simulate a weather and traffic conditions check
    if date == "2023-10-01" and location == "HIGH_TRAFFIC":
        return {"status": "suspicious", "message": "Unusual traffic conditions on the date."}
    return {"status": "clear", "message": "Normal weather and traffic conditions."}


@tool
def drivers_license_status_check(driver_license_number: Annotated[str, "claimant's driver license number."]):
    """
    Check the driver's license status.
    """
    # Simulate a driver's license status check
    return {"status": "clear", "message": "Driver's license is valid."}


