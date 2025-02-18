import ast, asyncio, json
from datetime import datetime
from pathlib import Path
from langchain_core.tools import tool, ToolException
from typing import Annotated, List, Dict, Any, Union
from src.pipelines.cost_benchmarking import AnalysisModelResultList, CostBenchmarking
from src.services.call_automation import AutomationServiceLogic
from src.services.dependencies.automation import AutomationServiceClient
from src.teams.fraud_detection.helper import (
    analysis_result_formatter,
)
from src.teams.resources.ssim import structural_similarity_index_measure
from src.rag.context_stuffing import process_query
from src.utilities.pdf_handlers import download_pdf
from typing_extensions import Annotated
from src.error_trace.errorlogger import system_logger
from decimal import InvalidOperation
from .test_vin_checker import VINValidator  # Import the VINValidator
from src.models.claim_processing import AccidentClaimData, TheftClaimData  # Import your Pydantic models

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

    async def _async_niid_call(registrationNumber: str):
        client = AutomationServiceLogic()
        niid_data = await client._run_niid_check(registrationNumber=registrationNumber)

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

    return asyncio.run(_async_niid_call(registrationNumber))

@tool
def check_vin(
    VehicleIdentificationNumber: Annotated[str, "The Identification number of the vehicle."],
    vehicleMake: Annotated[str, "The Manufacturer of the Vehicle. eg. Hyundai,Honda."],
    yearOfManufacture: Annotated[str, "The Year the Vehicle was Manufactured."],
    
    claim_data: Annotated[Union[AccidentClaimData, TheftClaimData], "Claim data for comparison."]
):
    """
    This tool calls the VIN validation logic to verify the vehicle identification number (VIN) and retrieve vehicle details.
    
    Args:
        VehicleIdentificationNumber (str): The VIN to validate.
        claim_data (Union[AccidentClaimData, TheftClaimData]): The claim data to compare against.
        
    Returns:
        Dict[str, Any]: Validation results with detailed information.
    """
    vin_validator = VINValidator()  # Instantiate the VINValidator
    result = vin_validator.validate_vin(VehicleIdentificationNumber)  # Validate the VIN

    # Initialize comparison status
    comparison_status = "error"
    
    # Compare the results with the claim data
    if result['status'] == 'success':
        manufacturer_match = claim_data.vehicleMake.lower() in result['manufacturer'].lower()
        model_year_match = result['model_year'] == claim_data.yearOfManufacture
        make_match = result['make'] == claim_data.vehicleMake
        model_match = result['model'] == claim_data.vehicleModel

        # Set comparison status to success if any match is found
        if manufacturer_match and model_year_match and make_match or model_match:
            comparison_status = "success"

    # Return the result with comparison status
    return {
        "status": comparison_status,
        "vin_validation": result,
        "comparison": {
            "manufacturer_match": manufacturer_match,
            "model_year_match": model_year_match,
            "make_match": make_match,
            "model_match": model_match,
        }
    }

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



@tool
def item_cost_price_benchmarking_in_local_market(
    the_vehicleMake_and_vehicleModel_and_vehicleBody_and_yearOfManufacture_and_damaged_part_list: Annotated[
        str,
        """the search term for the local market
*Instruction*
- It MUST be a nested list of the vehicle make vehicle model manufacture year and the damaged part against the quoted cost for the damaged part. e.g '[['hyundai sonata 2015 side mirror',49000],['hyundai sonata 2015 door handle',23000]]'

Bad search term(add driver):
❌ "[['Hyundai sonata 2015 driver side mirror',23000],['Hyundai sonata 2015 door panel',23000]]"

Good search term(no content and good nested list):
✅ "[['Hyundai sonata sedan', 2015, 'side mirror',23000],['Hyundai sonata sedan', 2015, 'door panel',23000]]"
""",
    ],
) -> str:
    """Benchmarks quoted cost for vehicle repairs against local market prices."""

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

        parsed_list = ast.literal_eval(
            the_vehicleMake_and_vehicleModel_and_vehicleBody_and_yearOfManufacture_and_damaged_part_list
        )
        
        updated_parsed_list: List[list] = []
        analysis_result_list: List = []
        # Define conditions
        conditions = ["tokunbo", "brand new"]
        for item in parsed_list:
            results = []
            for condition in conditions:
                validator(item[0], item[-1])
                updated_parsed_list.append(
                    [" ".join([item[0], condition]), item[1], item[2]]
                )
         
                make, model, body = item[0].split(" ")
                year = item[1]
                part = item[2]
                quoted_price = item[-1]
                cbm = CostBenchmarking(
                    make, model, body, int(year), part, quoted_price, condition
                )
                analysis = cbm.run_analysis()
                if analysis is None:
                    continue
                results.append(analysis)

            # Fill in missing results with values from other condition
            if len(results) == 2:
                if (
                    results[0].result == "no result"
                    and results[0].priceRange
                    == "no price range"
                ):
                    results[0].result = (
                        results[1].result
                    )
                    results[0].priceRange = (
                        results[1].priceRange
                    )
                elif (
                    results[1].result == "no result"
                    and results[1].priceRange
                    == "no price range"
                ):
                    results[1].result = (
                        results[0].result
                    )
                    results[1].priceRange = (
                        results[0].priceRange
                    )
            analysis_result_list.extend(results)

        analysisModelResultList = AnalysisModelResultList(analysisResult=analysis_result_list)
        
        formatted_results = analysis_result_formatter(
            conditions, updated_parsed_list, analysisModelResultList.analysisResult
        )
        print(formatted_results)
        return formatted_results

    except ToolException as e:
        system_logger.error(error=f"Validation error: {e}")
        return ToolException(str(e))
    except Exception as e:
        system_logger.error(error=f"Error in benchmarking: {e}")
        return ToolException(
            "An error occurred while benchmarking the cost. Please try again."
        )


@tool
def item_pricing_evaluator(
    vehicleMake: Annotated[str, "vehicle manufacturer name"],
    vehicleModel: Annotated[str, "vehicle model name"],
    vehicleBody: Annotated[str, "vehicle body type"],
    yearOfManufacture: Annotated[int, "year vehicle was manufactured"],
    damagedPart: Annotated[str, "the part of the vehicle that was damaged"],
) -> str:
    """Evaluates cost ranges for vehicle parts in the local market."""

    try:
        results = {}
        conditions = ["fairly used", "brand new"]
        for condition in conditions:
            cbm = CostBenchmarking(
                vehicleMake,
                vehicleModel,
                vehicleBody,
                int(yearOfManufacture),
                damagedPart,
                "",
                condition,
            )
            damage_cost = cbm._fetch_query()
            if damage_cost is None:
                results.update({" ".join([damagedPart, condition]): damage_cost})
                continue
            results.update({" ".join([damagedPart, condition]): damage_cost})
        return results
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
