
import os
from langchain_core.tools import tool
from typing import Annotated, Any, Dict, List, Union
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from src.teams.resources.image_understanding import SSIM
from src.rag.context_stuffing import process_query
from src.teams.resources.cost_benchmarking import CostBenchmarking
from src.teams.resources.retrieve_vehicle_policy import InsuranceDataExtractor


############## Fraud checks tool ##############


@tool
def verify_this_claimant_exists_as_a_customer(
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
def investigate_if_this_claimant_is_attempting_a_rapid_policy_claim(date_claim_filed: Annotated[str, "date this claim was filed"]):
    """
    Use this tool to check for rapid policy claims; to verify the claimant is not making a claim right after creating an insuring this vehicle.
    """
    # Retrieve
    query = f"this claim is/was filed: {date_claim_filed}.\nRespond with only the date the policy start in this format November 16, 2024, and do nothing else. interprete the insurance period as DD/MM/YYYY."
    resp = process_query(query=query)
  
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
        print(claimant_incident_detail)
        print("\n", ssim_data)
        resp = SSIM(claimant_incident_detail,ssim_data)
        return resp
    except Exception as e:
        return {"status": "error", "message": str(e)}

verify_vehicle_matches_preloss_using_SSIM = StructuredTool.from_function(
    func=verify_vehicle_matches_preloss_using_SSIM_func,
    name="Calculator",
    description="verify if vehicle matches preloss using structured similarity index",
    args_schema=SSIMInput,
    return_direct=True,
)
# @tool
# def verify_vehicle_matches_preloss_using_SSIM(
#     ssim_data: Annotated[Any, "the ssim data from the claim form json."],
#     claimant_incident_detail: Annotated[str, "the description of the incident that happened to the user e.g. A reckless driver hit my car from behind and broke breaking my rear lights."],
# ):
#     """
#     Use this tool to verify if the damages in the claim being filed for this vehicle matches its pre-loss condition using Structural Similarity Index (SSIM).
    
#     Args:
#     policy_number (str): The claimant's policy number.
#     claimant_incident_detail (str): A description of the incident that happened to the user, e.g., "A reckless driver hit my car from behind and broke my rear lights."
#     the_url_in_evidenceSourceUrl_of_the_damaged_vehicle_from_the_evidenceProvided_json (str): The URL of the evidence source of the damaged vehicle to be reviewed.
    
#     Returns:
#     dict: A response indicating the result of the SSIM analysis, or an error message if the process fails.
#     """
#     try:

#         print(claimant_incident_detail)
#         print("\n", ssim_data)
#         resp = SSIM(claimant_incident_detail,ssim_data)
#         return resp
#     except Exception as e:
#         return {"status": "error", "message": str(e)}

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
def vehicle_chasis_number_matches_NIID_records(vehicle_chasis_number: Annotated[str, "vehicle chasis number"]):
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

market_price = {}

@tool
def item_cost_price_benchmarking_in_local_market(
    vehicle_name_and_model_and_damaged_part: Annotated[str, "search for the damaged parts from the supporting evidence picture using this term `{{vehicle_name}} {{damaged_part}}. e.g Honda civic side mirror"],
    quoted_cost: Annotated[str, "the quoted cost from supporting evidence like invoice, required to fix the damage."]
) -> str:
    """
    Benchmarks the quoted cost for vehicle repairs against local market prices.
    """
    email = "sam@masteryhive.ai"
    password = "JLg8m4aQ8n46nhC"
    
    # Create separate instances for each search to avoid sharing state
    tokunbo_benchmarking = CostBenchmarking(email, password)
    brand_new_benchmarking = CostBenchmarking(email, password)

    try:
        import threading
        global market_price
        def fetch_tokunbo_prices():
            nonlocal tokunbo_prices
            tokunbo_prices = tokunbo_benchmarking.fetch_market_data(f"{vehicle_name_and_model_and_damaged_part} tokunbo")

        def fetch_brand_new_prices():
            nonlocal brand_new_prices
            brand_new_prices = brand_new_benchmarking.fetch_market_data(f"{vehicle_name_and_model_and_damaged_part} brand new")

        tokunbo_prices = []
        brand_new_prices = []

        thread_tokunbo = threading.Thread(target=fetch_tokunbo_prices)
        thread_brand_new = threading.Thread(target=fetch_brand_new_prices)

        thread_tokunbo.start()
        thread_brand_new.start()

        thread_tokunbo.join()
        thread_brand_new.join()
        market_price = {
            "tokunbo": tokunbo_prices,
            "brand_new": brand_new_prices
        }
        # Only analyze if we got prices
        if tokunbo_prices and brand_new_prices:
            quoted_cost_value = float(quoted_cost.replace(",", ""))
            tokunbo_analysis = tokunbo_benchmarking.analyze_price(tokunbo_prices, quoted_cost_value)
            brand_new_analysis = brand_new_benchmarking.analyze_price(brand_new_prices, quoted_cost_value)
            return f"FAIRLY USED (Tokunbo):\n{tokunbo_analysis}\n\nBRAND NEW:\n{brand_new_analysis}"
        else:
            return "Unable to fetch market prices. Please try again later."

    except Exception as e:
        print(f"Error in benchmarking: {e}")
        return "An error occurred while benchmarking the cost. Please try again later."


@tool
def item_pricing_evaluator(
    damaged_part: Annotated[str, "from the picture evidence which parts are damaged. e.g toyota corolla bumper"],
):
    """
     this cost evaluation tool checks the local market place for how much the damaged part is worth.
    """
    try:
        costBenchmarking = CostBenchmarking()
        result = costBenchmarking.run_with_expected_range(damaged_part,market_price)
        return result
    except Exception as e:
        return "sorry, this tool can not be used at the moment"


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



# @tool
# #def fraud_detection_tool(risk_indicators: Annotated[str, "the weights from each tool used in a list. e.g [0.12,0.15,0.13,0.18,0.12,0.05,0.10,0.15]"]) -> str:
# def fraud_detection_tool(risk_indicators: Annotated[dict, 'A JSON string of risk indicators from fraud detection tools e.g {"claimant_exists": 0.12, "policy_status_check": 0.15, "vehicle_insurance_check": 0.13, "item_pricing_benchmarking": 0.18, "ghost_claims_vehicle_check": 0.12, "vehicle_registration_match": 0.05, "rapid_policy_claims_check": 0.10, "drivers_license_status_check": 0.15}']) -> Dict[str, Union[Dict[str, float], float, Dict[str, bool]]]:
#     """
#     This tool is used to calculate the fraud risk score from the weights of the investigator checks.
#     """
#     # Predefined weights for each fraud detection tool
#     weights = {
#         "claimant_exists": 0.12,
#         "policy_status_check": 0.15,
#         "vehicle_insurance_check": 0.13,
#         "item_pricing_benchmarking": 0.18,
#         "ghost_claims_vehicle_check": 0.12,
#         "vehicle_registration_match": 0.05,
#         "rapid_policy_claims_check": 0.10,
#         "drivers_license_status_check": 0.15,
#     }
    
#     # Validate input matches expected tools
#     if set(risk_indicators.keys()) != set(weights.keys()):
#         return "Mismatch between input indicators and expected fraud risk indicators. Please check your input!"
    
#     # Risk scoring
#     risk_scores = {}
#     total_risk_score = 0
#     results = {}
    
#     # Calculate risk for each tool
#     for tool, result in risk_indicators.items():
#         # Determine if the tool indicates potential fraud
#         is_fraud_indicator = result < weights[tool]
        
#         # Calculate risk score based on tool result and weight
#         if is_fraud_indicator:
#             tool_risk_score = weights[tool]
#             total_risk_score += tool_risk_score
#             risk_scores[tool] = tool_risk_score
#             results[tool] = False
#         else:
#             risk_scores[tool] = result
#             results[tool] = True
    
#     # Final risk score as a percentage
#     final_risk_score = f"{total_risk_score:.0%}"  # Cap at 100%
#     if total_risk_score <=15:
#         fraud_level = "LOW"
#     elif total_risk_score <= 50:
#         fraud_level = "MEDIUM"
#     else:
#         fraud_level = "HIGH"
#     res = {
#         "indicator_risk_scores": risk_scores,
#         "fraud_risk_score": final_risk_score,
#         "indicators_used": results,
#         "fraud_risk_level": fraud_level,
#     }
#     return res

# implement SSIM