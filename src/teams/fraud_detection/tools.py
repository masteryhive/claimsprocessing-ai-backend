from datetime import datetime
import json
from pathlib import Path
from langchain_core.tools import tool
from typing import Annotated
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from src.teams.resources.ssim import structural_similarity_index_measure
from src.rag.context_stuffing import process_query
from src.teams.resources.cost_benchmarking import CostBenchmarkingPlaywright
from src.teams.resources.retrieve_vehicle_policy import InsuranceDataExtractor
from src.utilities.pdf_handlers import download_pdf
from typing import TypedDict
############## Fraud checks tool ##############
rag_path = Path(__file__).parent.parent / "policy_doc/"


@tool
def verify_this_claimant_exists_as_a_customer(
    policyNumber: Annotated[str, "claimant's policy number."],
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
def investigate_if_this_claimant_is_attempting_a_rapid_policy_claim(
    dateClaimFiled: Annotated[str, "date this claim was filed"],
    policyNumber: Annotated[str, "the claimant's policy number"],
):
    """
    Use this tool to check for rapid policy claims; to verify the claimant is not making a claim right after creating an insuring this vehicle.
    Args:
        policyNumber (str): The claimant's policy number.
        dateClaimFiled: (str): The date this claim was filed.
    """
    # Retrieve
    download_pdf(policyNumber, rag_path)
    # Define the response schema for the query
    response_schema = {
        "type": "object",
        "properties": {
            "PolicyPeriod": {
                "type": "object",
                "properties": {
                    "From": {
                        "type": "string",
 "description": "The start date of the policy period, typically found in sections labeled 'policy period' or 'coverage dates'. Input date should be interpreted in DD/MM/YYYY format (e.g., 06/11/2024) and converted to format 'Month DD, YYYY' (e.g., November 6, 2024)",
                    },
                },
                "required": ["From"],
            },
        },
        "required": ["PolicyPeriod"],
    }

    query = (
        f"this claim is/was filed: {dateClaimFiled}.",
        "\nPlease respond with only the date the policy start in this format November 16, 2024, and Do not include any additional information or commentary.",
        "\nThe current date(YYYY-MM-DD) is {current_date}.",
    )
    resp = process_query(
        prompt="".join(query),
        pdf_path=f"{rag_path}/{policyNumber.replace("/", "-")}.pdf",
        response_schema=response_schema,
    )

    def calc(date_claim_filed:str, resp:str):
        # Extract the date from the response
        start_date_str = json.loads(resp)["PolicyPeriod"]["From"]
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

    return calc(dateClaimFiled, resp)


############## vehicle fraud ##################
@tool
def validate_if_this_is_a_real_vehicle(
    vehicle_information: Annotated[
        str, "vehicle make and brand. e.g toyota corolla 2012"
    ]
):
    """
    Check if the provided vehicle information corresponds to a real vehicle to mitigate ghost vehicle claims.
    """
    # Simulate a check for ghost claims
    return {"status": "clear", "message": "This vehicle is valid."}

@tool
def check_NIID_database_(
    registrationNumber: Annotated[str, "The registration number of the vehicle."],
    chasisNumber: Annotated[str, "The chassis number of the vehicle."]
):
    """
    this tool calls the NIID database to see if the vehicle has been insured using the registrationNumber and verifies that the vehicle chasis matches NIID internal database records.
    """
    niid_data = {}
    extractor = InsuranceDataExtractor(registrationNumber.strip().lower())
    niid_data = extractor.run()
    if niid_data.get("status") == "success":
        niid_data["check_NIID_database_result"]={"existing_insurance_check_message": "Yes, this vehicle has an existing insurance record in the NIID database"}
    else:
        niid_data["check_NIID_database_result"]={"existing_insurance_check_message": "No, this vehicle does not have an existing insurance record in the NIID database"}
    if (
        niid_data.get("status") == "success"
        and niid_data.get("data")["ChassisNumber"].lower() == chasisNumber.strip().lower()
    ):
        niid_data["check_NIID_database_result"].update({"chasis_check_message":
            "Yes, this vehicle chasis number matches NIID internal database records"}
        )
    elif (
        niid_data.get("status") == "success"
        and niid_data.get("data")["ChassisNumber"].lower() != chasisNumber.strip().lower()
    ):
        niid_data["check_NIID_database_result"].update({"chasis_check_message":
         "No, this vehicle chasis number does not match NIID internal database records"}
        )
    else:
        niid_data["check_NIID_database_result"].update({"chasis_check_message":
            "No, this vehicle has no record in NIID internal database records, therefore chasis number can not be checked against NIID record."}
        )
    extractor.driver_pool.shutdown() #shutdown driver pool for cleanup
    return niid_data["check_NIID_database_result"]

@tool
def ssim(
    prelossImageUrl: Annotated[str,"The URL of the pre-loss condition image."], 
    damageConditionImageUrl: Annotated[str,"The URL of the vehicle showing the damage condition for this claim."],
    incidentDetails: Annotated[str,'A description of the incident that happened to the user, e.g., "A reckless driver hit my car from behind and broke my rear lights."']
) -> str:
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
        ssim_data = [{"prelossUrl": prelossImageUrl.replace("https://storage.googleapis.com","gs://"), "claimUrl": damageConditionImageUrl.replace("https://storage.googleapis.com/","gs://")}]
        resp = structural_similarity_index_measure(incidentDetails, ssim_data)
        return resp
    except Exception as e:
        return {"status": "error", "message": str(e)}


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
    quoted_cost: Annotated[str, "quoted cost"],
) -> str:
    """
    Benchmarks the quoted cost for vehicle repairs against local market prices.
    """
    benchmarking = get_benchmarking_instance()

    try:
        # print(vehicle_name_and_model_and_damaged_part,quoted_cost)
        quoted_cost = quoted_cost.replace("\u20a6", "").replace(",", "")
        quoted_cost = quoted_cost if quoted_cost != "None" else 0
        quoted_cost_value = float(quoted_cost)

        global market_prices

        tokunbo_prices = benchmarking.fetch_market_data(
            f"{vehicle_name_and_model_and_damaged_part} tokunbo"
        )
        brand_new_prices = benchmarking.fetch_market_data(
            f"{vehicle_name_and_model_and_damaged_part} brand new"
        )

        market_prices = {"tokunbo": tokunbo_prices, "brand_new": brand_new_prices}

        if tokunbo_prices and brand_new_prices:
            tokunbo_analysis = benchmarking.analyze_price(
                tokunbo_prices, quoted_cost_value
            )
            brand_new_analysis = benchmarking.analyze_price(
                brand_new_prices, quoted_cost_value
            )
            # print(f"FAIRLY USED (Tokunbo):\n{tokunbo_analysis}\n\nBRAND NEW:\n{brand_new_analysis}")
            return f"FAIRLY USED (Tokunbo):\n{tokunbo_analysis}\n\nBRAND NEW:\n{brand_new_analysis}"
        return "Unable to fetch market prices. Please try again."
    except Exception as e:
        print(f"Error in benchmarking: {e}")
        return "An error occurred while benchmarking the cost. Please try again."


@tool
def item_pricing_evaluator(
    vehicle_name_and_model_and_damaged_part: Annotated[str, "search term"]
):
    """
    this cost evaluation tool checks the local market place for how much the damaged part is worth.
    """
    benchmarking = get_benchmarking_instance()
    try:
        if market_prices:
            tokunbo_analysis = benchmarking.run_with_expected_range(
                vehicle_name_and_model_and_damaged_part, market_prices["tokunbo"]
            )
            brand_new_analysis = benchmarking.run_with_expected_range(
                vehicle_name_and_model_and_damaged_part, market_prices["brand_new"]
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
        return {
            "status": "suspicious",
            "message": "Unusual traffic conditions on the date.",
        }
    return {"status": "clear", "message": "Normal weather and traffic conditions."}


@tool
def drivers_license_status_check(
    driver_license_number: Annotated[str, "claimant's driver license number."]
):
    """
    Check the driver's license status.
    """
    # Simulate a driver's license status check
    return {"status": "clear", "message": "Driver's license is valid."}
