import json
from typing import Annotated, Dict, Union
from langchain_core.tools import tool
from src.ai.resources.cost_benchmarking import CostBenchmarking
from src.ai.resources.retrieve_vehicle_policy import InsuranceDataExtractor
from src.ai.resources.image_understanding import claims_image_evidence_recognizer
from src.config.appconfig import env_config


email = "sam@masteryhive.ai"
password = "JLg8m4aQ8n46nhC"

############## document extraction and completeness check ##############
@tool
def supporting_document_understanding(
    document_url: Annotated[str, "supporting document URL"],
):
    """
    Analyzes the document to determine what it is using the document URL.
    """
    return claims_image_evidence_recognizer(document_url)


@tool
def claims_document_completeness(policy_number: Annotated[str, "policy_number"]):
    """
    retrieve document completion status using policy_id
    """
    # Implement a logic to mock the different files
    res = f"""
    Claimant's policy ID: {policy_number}
    * The provided driver's license matches the name on the claim form.
    * The provided police report confirms the accident details.
    * The provided vehicle registration matches the vehicle on the claim form.
    ===
    {{"claims_document_completeness_status":"documents are complete!"}}
    """
    return res


############## Fraud checks tool ##############


@tool
def claimant_exists(
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
def policy_status_check(policy_number: Annotated[str, "claimant's policy_number."]):
    """
    checks if the status of the claimant's insurance policy is active using the policy_id
    """
    # Implement the policy status check logic here
    return {"status": "success", "message": f"Policy ID: {policy_number} is active!"}


@tool
def item_insurance_check(
    vehicle_registration_number: Annotated[
        str, "claimant's vehicle registration number."
    ]
):
    """
    calls the NIID database to see if the vehicle has been insured using the vehicle registration number.
    """
    try:
        extractor = InsuranceDataExtractor(vehicle_registration_number)
        try:
            # Call the method to perform the extraction
            data = extractor.extract_data()
        finally:
            # Ensure the driver is closed after extraction
            extractor.close_driver()
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        extractor.close_driver()


@tool
def item_pricing_benmarking(
    damaged_part: Annotated[str, "Identify the damaged parts from the supporting evidence picture. e.g Honda civic side mirror"],
    quoted_cost: Annotated[str, "the quoted cost from supporting evidence like invoice, required to fix the damage."]
):
    """
    this cost benchmarking tool calls the local market place to verify the quoted cost on the invoice for the vehicle repair claims.
    """
    costBenchmarking = CostBenchmarking(email=email,password=password)
    result = costBenchmarking.run(damaged_part, quoted_cost)
    print(result)
    return result


@tool
def item_pricing_evaluator(
    damaged_part: Annotated[str, "from the picture evidence which parts are damaged. e.g toyota corolla bumper"],
):
    """
     this cost evaluation tool checks the local market place for how much the damaged part is worth.
    """
    costBenchmarking = CostBenchmarking(email=email,password=password)
    result = costBenchmarking.run_with_expected_range(damaged_part)
    print(result)
    return result



@tool
def ghost_claims_check(vehicle_information: Annotated[str, "vehicle make and brand. e.g toyota corolla 2012"]):
    """
    Check for non-existent vehicles.
    """
    # Simulate a check for ghost claims
    return {"status": "clear", "message": "This vehicle is valid."}

@tool
def vehicle_registration_match(policy_number: Annotated[str, "claimant's policy_number."],
                               vehicle_registration_number: Annotated[str, "vehicle registration number"]):
    """
    Verify vehicle registration matches internal database records.
    """
    # Simulate a registration match check
    return {"status": "success", "message": "Registration number matches records."}


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
def rapid_policy_claims_check(policy_number: Annotated[str, "claimant's policy_number."], 
                              date_of_claim: Annotated[str, "date this claim is filed"],):
    """
    Check for rapid policy claims, to verify the claimant is not making a claim right after creating an insurance account.
    """
    # Simulate a rapid policy claims check
    return {"status": "clear", "message": "Claim date is normal."}

@tool
def drivers_license_status_check(driver_license_number: Annotated[str, "claimant's driver license number."]):
    """
    Check the driver's license status.
    """
    # Simulate a driver's license status check
    return {"status": "clear", "message": "Driver's license is valid."}


@tool
#def fraud_detection_tool(risk_indicators: Annotated[str, "the weights from each tool used in a list. e.g [0.12,0.15,0.13,0.18,0.12,0.05,0.10,0.15]"]) -> str:
def fraud_detection_tool(risk_indicators: Annotated[str, "A JSON string of risk indicators from fraud detection tools e.g {'claimant_exists': 0.12, 'policy_status_check': 0.15, 'item_insurance_check': 0.13, 'item_pricing_benchmarking': 0.18, 'ghost_claims_vehicle_check': 0.12, 'vehicle_registration_match': 0.05, 'rapid_policy_claims_check': 0.10, 'drivers_license_status_check': 0.15}"]) -> Dict[str, Union[Dict[str, float], float, Dict[str, bool]]]:
    """
    This tool is used to calculate potential fraud risk.
    """
    # Predefined weights for each fraud detection tool
    weights = {
        "claimant_exists": 0.12,
        "policy_status_check": 0.15,
        "item_insurance_check": 0.13,
        "item_pricing_benchmarking": 0.18,
        "ghost_claims_vehicle_check": 0.12,
        "vehicle_registration_match": 0.05,
        "rapid_policy_claims_check": 0.10,
        "drivers_license_status_check": 0.15,
    }
    
    # Parse the input risk indicators
    try:
        risk_indicators_dict = json.loads(risk_indicators)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON input for risk indicators")
    
    # Validate input matches expected tools
    if set(risk_indicators_dict.keys()) != set(weights.keys()):
        raise ValueError("Mismatch between input tools and expected fraud detection tools")
    
    # Risk scoring
    risk_scores = {}
    total_risk_score = 0
    results = {}
    
    # Calculate risk for each tool
    for tool, result in risk_indicators_dict.items():
        # Determine if the tool indicates potential fraud
        is_fraud_indicator = result < weights[tool]
        
        # Calculate risk score based on tool result and weight
        if is_fraud_indicator:
            tool_risk_score = weights[tool]
            total_risk_score += tool_risk_score
            risk_scores[tool] = tool_risk_score
            results[tool] = False
        else:
            risk_scores[tool] = result
            results[tool] = True
    
    # Final risk score as a percentage
    final_risk_score = f"{total_risk_score:.0%}"  # Cap at 100%
    if total_risk_score <=15:
        fraud_level = "LOW"
    elif total_risk_score <= 50:
        fraud_level = "MEDIUM"
    else:
        fraud_level = "HIGH"
    
    return {
        "individual_risk_scores": risk_scores,
        "final_risk_score": final_risk_score,
        "tool_results": results,
        "fraud_risk_level": fraud_level,
    }


# implement SSIM

############## claim summarizer ##############