import asyncio
from datetime import datetime
import json
from pathlib import Path
from langchain_core.tools import tool,StructuredTool,ToolException
from typing import Annotated,Optional, Dict, List, Any
from src.teams.resources.ssim import structural_similarity_index_measure
from src.rag.context_stuffing import process_query
from src.pipelines.local_markets.jiji.cost_benchmarking import CostBenchmarking
from src.pipelines.niid_check import InsuranceDataExtractor
from src.utilities.pdf_handlers import download_pdf
from typing_extensions import Annotated
from contextlib import asynccontextmanager
from src.error_trace.errorlogger import system_logger
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


async def check_NIID_database_(
    registrationNumber: Annotated[str, "The registration number of the vehicle."],
    chasisNumber: Annotated[str, "The chassis number of the vehicle."]
):
    """
    this tool calls the NIID database to see if the vehicle has been insured using the registrationNumber and verifies that the vehicle chasis matches NIID internal database records.
    """
    niid_data = {}
    extractor = InsuranceDataExtractor(registrationNumber.strip().lower())
    niid_data = await extractor.run()

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
    # Validate inputs
    if not prelossImageUrl or not damageConditionImageUrl or not incidentDetails:
        raise ToolException("All inputs (prelossImageUrl, damageConditionImageUrl, and incidentDetails) must be provided")

    prelossImageUrl = prelossImageUrl.strip()
    damageConditionImageUrl = damageConditionImageUrl.strip() 
    incidentDetails = incidentDetails.strip()

    if not prelossImageUrl or not damageConditionImageUrl or not incidentDetails:
        raise ToolException("All inputs must contain non-empty strings")
    try:
        ssim_data = [{"prelossUrl": prelossImageUrl.replace("https://storage.googleapis.com","gs://"), "claimUrl": damageConditionImageUrl.replace("https://storage.googleapis.com/","gs://")}]
        resp = structural_similarity_index_measure(incidentDetails, ssim_data)
        return resp
    except Exception as e:
        return {"status": "error", "message": str(e)}


############## damage cost fraud ##################

class BenchmarkingToolkit:
    _instance: Optional['BenchmarkingToolkit'] = None
    _benchmarking: Optional[CostBenchmarking] = None
    _market_prices: Dict[str, List[float]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    @asynccontextmanager
    async def get_benchmarking(cls):
        if cls._benchmarking is None:
            cls._benchmarking = CostBenchmarking(
                email="sam@masteryhive.ai",
                password="JLg8m4aQ8n46nhC"
            )
            await cls._benchmarking.__aenter__()
        try:
            yield cls._benchmarking
        except Exception as e:
            system_logger.error(f"Error in benchmarking context: {e}")
            raise
    
    @classmethod
    async def cleanup(cls):
        if cls._benchmarking:
            await cls._benchmarking.__aexit__(None, None, None)
            cls._benchmarking = None

    @classmethod
    def parse_quoted_cost(cls, quoted_cost: str) -> float:
        quoted_cost = quoted_cost.replace("\u20a6", "").replace(",", "")
        return float(quoted_cost if quoted_cost != "None" else 0)

    @classmethod
    async def fetch_prices(cls, search_term: str) -> Dict[str, List[float]]:
        async with cls.get_benchmarking() as benchmarking:
            tokunbo_prices = await benchmarking.analyze_market_price(
                f"{search_term} tokunbo", 0
            )
            brand_new_prices = await benchmarking.analyze_market_price(
                f"{search_term} brand new", 0
            )
            cls._market_prices = {
                "tokunbo": tokunbo_prices,
                "brand_new": brand_new_prices
            }
            return cls._market_prices


async def item_cost_price_benchmarking_in_local_market(
    vehicle_name_and_model_and_damaged_part: Annotated[str, "search term"],
    quoted_cost: Annotated[str, "quoted cost"],
) -> str:
    """Benchmarks quoted cost for vehicle repairs against local market prices."""
    toolkit = BenchmarkingToolkit()
    
    try:
        quoted_cost_value = toolkit.parse_quoted_cost(quoted_cost)
        market_prices = await toolkit.fetch_prices(vehicle_name_and_model_and_damaged_part)
        
        async with toolkit.get_benchmarking() as benchmarking:
            tokunbo_analysis = await benchmarking.analyze_market_price(
                f"{vehicle_name_and_model_and_damaged_part} tokunbo",
                quoted_cost_value
            )
            brand_new_analysis = await benchmarking.analyze_market_price(
                f"{vehicle_name_and_model_and_damaged_part} brand new",
                quoted_cost_value
            )
            
        return f"FAIRLY USED (Tokunbo):\n{tokunbo_analysis}\n\nBRAND NEW:\n{brand_new_analysis}"
    
    except Exception as e:
        system_logger.error(f"Error in benchmarking: {e}")
        return "An error occurred while benchmarking the cost. Please try again."



async def item_pricing_evaluator(
    vehicle_name_and_model_and_damaged_part: Annotated[str, "search term"]
) -> str:
    """Evaluates cost ranges for vehicle parts in the local market."""
    toolkit = BenchmarkingToolkit()
    
    try:
        if not toolkit._market_prices:
            await toolkit.fetch_prices(vehicle_name_and_model_and_damaged_part)
            
        async with toolkit.get_benchmarking() as benchmarking:
            tokunbo_range = benchmarking.analyzer.get_expected_price_range(
                toolkit._market_prices["tokunbo"]
            )
            brand_new_range = benchmarking.analyzer.get_expected_price_range(
                toolkit._market_prices["brand_new"]
            )
            
        return (
            f"FAIRLY USED (Tokunbo):\nExpected price range: {tokunbo_range}\n\n"
            f"BRAND NEW:\nExpected price range: {brand_new_range}"
        )
    
    except Exception as e:
        system_logger.error(f"Error in price evaluation: {e}")
        return "Price evaluation unavailable at this time"


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
