import ast
import asyncio
from datetime import datetime
import json
from pathlib import Path
from langchain_core.tools import tool, StructuredTool, ToolException
from typing import Annotated, Optional, Dict, List, Any
from src.services.call_automation import AutomationServiceLogic, MarketSearchModel
from src.teams.fraud_detection.helper import AnalysisModelResultList, analysis_result_formatter
from src.teams.resources.ssim import structural_similarity_index_measure
from src.rag.context_stuffing import process_query
from src.pipelines.niid_check import InsuranceDataExtractor
from src.utilities.pdf_handlers import download_pdf
from typing_extensions import Annotated
from contextlib import asynccontextmanager
from src.error_trace.errorlogger import system_logger
from decimal import Decimal, InvalidOperation

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

    def calc(date_claim_filed: str, resp: str):
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
def check_niid_database(
    registrationNumber: Annotated[str, "The registration number of the vehicle."],
    chasisNumber: Annotated[str, "The chassis number of the vehicle."],
):
    """
    this tool calls the NIID database to see if the vehicle has been insured using the registrationNumber and verifies that the vehicle chasis matches NIID internal database records.
    """
    niid_data = {}
    try:
        # Validate chasisNumber
        if not isinstance(chasisNumber, str) or not chasisNumber.strip():
            raise ToolException("Invalid chasisNumber: must be a non-empty string")

        # Validate registrationNumber
        if not isinstance(registrationNumber, str) or not registrationNumber.strip():
            raise ToolException(
                "Invalid registrationNumber: must be a non-empty string"
            )

    except ToolException as e:
        raise e

    async def async_task():
        extractor = InsuranceDataExtractor(registrationNumber.strip().lower())
        return await extractor.run()

    niid_data = asyncio.run(async_task())

    if niid_data.get("status") == "success":
        niid_data["check_NIID_database_result"] = {
            "existing_insurance_check_message": f"Yes, this vehicle has an existing insurance record in the NIID database with this certificate: {niid_data.get("data")["InsuranceCerticateNumber"]}"
        }
    else:
        niid_data["check_NIID_database_result"] = {
            "existing_insurance_check_message": "No, this vehicle does not have an existing insurance record in the NIID database"
        }
    if (
        niid_data.get("status") == "success"
        and niid_data.get("data")["ChassisNumber"].lower()
        == chasisNumber.strip().lower()
    ):
        niid_data["check_NIID_database_result"].update(
            {
                "chasis_check_message": "Yes, this vehicle chasis number matches NIID internal database records"
            }
        )
    elif (
        niid_data.get("status") == "success"
        and niid_data.get("data")["ChassisNumber"].lower()
        != chasisNumber.strip().lower()
    ):
        niid_data["check_NIID_database_result"].update(
            {
                "chasis_check_message": "No, this vehicle chasis number does not match NIID internal database records"
            }
        )
    else:
        niid_data["check_NIID_database_result"].update(
            {
                "chasis_check_message": "No, this vehicle has no record in NIID internal database records, therefore chasis number can not be checked against NIID record."
            }
        )

    return niid_data["check_NIID_database_result"]


@tool
def ssim(
    prelossImageUrl: Annotated[str, "The URL of the pre-loss condition image."],
    damageConditionImageUrl: Annotated[
        str, "The URL of the vehicle showing the damage condition for this claim."
    ],
    incidentDetails: Annotated[
        str,
        'A description of the incident that happened to the user, e.g., "A reckless driver hit my car from behind and broke my rear lights."',
    ],
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
        raise ToolException(
            "All inputs (prelossImageUrl, damageConditionImageUrl, and incidentDetails) must be provided"
        )

    prelossImageUrl = prelossImageUrl.strip()
    damageConditionImageUrl = damageConditionImageUrl.strip()
    incidentDetails = incidentDetails.strip()

    if not prelossImageUrl or not damageConditionImageUrl or not incidentDetails:
        raise ToolException("All inputs must contain non-empty strings")
    try:
        ssim_data = [
            {
                "prelossUrl": prelossImageUrl.replace(
                    "https://storage.googleapis.com", "gs://"
                ),
                "claimUrl": damageConditionImageUrl.replace(
                    "https://storage.googleapis.com/", "gs://"
                ),
            }
        ]
        resp = structural_similarity_index_measure(incidentDetails, ssim_data)
        return resp
    except Exception as e:
        return {"status": "error", "message": str(e)}


############## damage cost fraud ##################

market_prices = {}


async def aitem_cost_price_benchmarking_in_local_market(
    list_of_vehicle_name_and_model_and_damaged_part: List[list],
) -> str:
    """Benchmarks quoted cost for vehicle repairs against local market prices."""
    global market_prices
    try:

        def validator(vehicle_name_and_model_and_damaged_part: str, quoted_cost: str):
            # Validate vehicle_name_and_model_and_damaged_part
            if (
                not isinstance(vehicle_name_and_model_and_damaged_part, str)
                or not vehicle_name_and_model_and_damaged_part.strip()
            ):
                raise ToolException(
                    "Invalid vehicle_name_and_model_and_damaged_part: must be a non-empty string"
                )

            # Validate quoted_cost
            try:
                quoted_cost_value = float(quoted_cost)
            except (InvalidOperation, TypeError):
                raise ToolException(
                    "Invalid quoted_cost: must be a valid decimal number"
                )

        parsed_list = ast.literal_eval(list_of_vehicle_name_and_model_and_damaged_part)
        updated_parsed_list: List[list] = []

        # Define conditions
        conditions = ["fairly used", "brand new"]

        for item in parsed_list:
            for condition in conditions:
                validator(item[0], item[1])
                new_item = [f"{item[0]} {condition}", float(item[1])]
                updated_parsed_list.append(new_item)
                
            marketSearchModel = MarketSearchModel(
                email="sam@masteryhive.ai",
                login_required=True,
                password="JLg8m4aQ8n46nhC",
                searchTerms=str(updated_parsed_list),
                target_market="jiji",
            )
            client = AutomationServiceLogic()
            results = client._run_market_search(marketSearchModel=marketSearchModel)
            print(results)
            print()
            analysisModelResultList = AnalysisModelResultList(**results)
            print(analysisModelResultList)
            print()
            formatted_results = analysis_result_formatter(
                conditions, updated_parsed_list, analysisModelResultList.analysisResult
            )
            print(formatted_results)
            return formatted_results

    except ToolException as e:
        system_logger.error(f"Validation error: {e}")
        return ToolException(str(e))
    except Exception as e:
        system_logger.error(f"Error in benchmarking: {e}")
        return ToolException(
            "An error occurred while benchmarking the cost. Please try again."
        )


@tool
def item_cost_price_benchmarking_in_local_market(
    the_vehicleMake_and_vehicleModel_and_yearOfManufacture_and_damaged_part_list: Annotated[
        str,
        "search term, it MUST be a nested list of the vehicle make vehicle model manufacture year and the damaged part against the quoted cost for the damaged part. e.g '[['hyundai sonata 2015 side mirror',49000],['hyundai sonata 2015 door handle',23000]]'",
    ],
) -> str:
    """Synchronous wrapper for the async benchmarking function."""

    system_logger.info(
        f"{the_vehicleMake_and_vehicleModel_and_yearOfManufacture_and_damaged_part_list}"
    )

    return asyncio.run(
        aitem_cost_price_benchmarking_in_local_market(
            the_vehicleMake_and_vehicleModel_and_yearOfManufacture_and_damaged_part_list
        )
    )



@tool
def item_pricing_evaluator(
    vehicle_name_and_model_and_damaged_part: Annotated[str, "search term"]
) -> str:
    """Evaluates cost ranges for vehicle parts in the local market."""

    try:

        # async def async_task():
        #     async with CostBenchmarking(
        #         email="sam@xxxx", password="xxxx"
        #     ) as benchmarking:
        #         tokunbo_range = benchmarking.analyzer.get_expected_price_range(
        #             market_prices["fairly_used"]
        #         )
        #         brand_new_range = benchmarking.analyzer.get_expected_price_range(
        #             market_prices["brand_new"]
        #         )

        #     return (
        #         f"FAIRLY USED (Tokunbo):\nExpected price range: {tokunbo_range}\n\n"
        #         f"BRAND NEW:\nExpected price range: {brand_new_range}"
        #     )

        # return asyncio.run(async_task())
        print("no result")
    except Exception as e:
        system_logger.error(f"Error in price evaluation: {e}")
        return "Price evaluation unavailable at this time"


# ################### other checks ################
# @tool
# def claimant_location_check(claimant_id: str, location: str):
#     """
#     Check claimant's location.
#     """
#     # Simulate a location check
#     if location == "UNKNOWN":
#         return {"status": "suspicious", "message": "Claimant location is unknown."}
#     return {"status": "clear", "message": "Claimant location verified."}


# @tool
# def weather_traffic_conditions_check(date: str, location: str):
#     """
#     Check weather and traffic conditions.
#     """
#     # Simulate a weather and traffic conditions check
#     if date == "2023-10-01" and location == "HIGH_TRAFFIC":
#         return {
#             "status": "suspicious",
#             "message": "Unusual traffic conditions on the date.",
#         }
#     return {"status": "clear", "message": "Normal weather and traffic conditions."}


# @tool
# def drivers_license_status_check(
#     driver_license_number: Annotated[str, "claimant's driver license number."]
# ):
#     """
#     Check the driver's license status.
#     """
#     # Simulate a driver's license status check
#     return {"status": "clear", "message": "Driver's license is valid."}
