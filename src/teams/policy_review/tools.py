
from typing import Annotated
from langchain_core.tools import tool
from src.rag.context_stuffing import download_pdf, process_query
from src.utilities.helpers import _new_get_datetime

rag_path = "src/rag/doc/"

@tool
def download_policy_document_from_storage(policy_number: Annotated[str, "claimant's policy number."]):
    """
    Use this tool to first download the policy document from the storage using the claimant policy number.
    """
    return download_pdf(policy_number)

@tool
def retrieve_all_essential_details_from_policy(policy_number: Annotated[str, "claimant's policy number."]):
    """
    Use this tool to retrieve all essential details, including terms, policy status, and coverage plan or status.
    """
    # Retrieve
    query = (
        "Analyze this vehicle insurance policy document comprehensively and provide all critical information in a structured format. "
        "Extract and present the following details in very clear informative terms:\n\n"
        "1. Policy Basics:\n"
        " - Policy period/duration\n"
        " - Policy type and coverage category\n"
        " - Premium details (annual, paid amount, payment terms)\n"
        " - Policyholder details\n\n"
        "2. Vehicle Details:\n"
        " - Make, model, and year\n"
        " - Vehicle value/sum insured\n"
        " - Vehicle usage type (private/commercial)\n\n"
        "3. Coverage Details:\n"
        " - Main coverage types (comprehensive, third party, etc.)\n"
        " - Additional coverages/riders\n"
        " - Coverage limits and sub-limits\n"
        " - Authorized repair limits\n\n"
        "4. Key Terms and Conditions:\n"
        " - All policy conditions\n"
        " - Warranties\n"
        " - Special clauses\n"
        " - Endorsements\n\n"
        "5. Exclusions and Limitations:\n"
        " - Policy exclusions\n"
        " - Geographic limitations\n"
        " - Usage restrictions\n\n"
        "6. Claims and Notification Requirements:\n"
        " - Claims procedure\n"
        " - Notification period for valid claims\n"
        " - Required documentation for claims\n"
        " - Emergency contact numbers\n"
        " - No-claim bonus details\n"
        " - Time limits for claim submission\n"
        " - Reporting requirements for accidents/incidents\n\n"
        "7. Cancellation and Modification:\n"
        " - Cancellation terms and notice periods\n"
        " - Policy modification procedures\n"
        " - Refund conditions\n\n"
        "Important Instructions:\n"
        " - To begin, carefully look through the entire document and identify all the information you should extract as they are required.\n"
        " - Present each piece of information on a new line using `<br/>`\n"
        " - Tag each item with a dash (-)\n"
        " - Provide complete information without summarizing\n"
        " - Include all schedules and estimated values\n"
        " - List all memoranda, conditions, and clauses individually and not as summary\n"
        " - Do not mark any information as 'MISSING'\n"
        " - Do not redact or omit any information\n"
        " - Include any other important information found in the document even if not specifically requested above"
    )
    resp = process_query(query=query,pdf_path=f"{rag_path}{policy_number.replace("/", "-")}.pdf")
    return resp


@tool
def check_if_this_claim_is_within_insurance_period(policy_number: Annotated[str, "claimant's policy number."]):
    """
    Check if the current date falls within the specified insurance period.
    """
    # Retrieve

    query = f"confirm that the insured period is still active."
    resp = process_query(query=query,pdf_path=f"{rag_path}{policy_number.replace("/", "-")}.pdf")
    return resp

@tool
def check_if_this_claim_is_reported_within_insurance_period(date_of_incident: Annotated[str, "date the incident occured"],
                                                            policy_number: Annotated[str, "claimant's policy number."]):
    """
    Check if the claim is reported within the stipulated notification period.
    """
    # Retrieve
    query = f"\n the date the incident occured is {_new_get_datetime(date_of_incident)}. confirm that the claim is within the stipulated notification period."
    resp = process_query(query=query,pdf_path=f"{rag_path}{policy_number.replace("/", "-")}.pdf")
    return resp

@tool
def check_if_the_incident_occurred_within_the_geographical_coverage(location_of_incident: Annotated[str, "location where the incident occurred, default is Lagos, Nigeria"],
                                                                    policy_number: Annotated[str, "claimant's policy number."]):
    """
    Check if the incident occurred within the geographical area covered by the policy.
    """
    # Retrieve
    query = f"\n the incident occurred in Lagos, Nigeria. confirm if the incident occurred within the geographical area covered by the policy."
    resp = process_query(query=query,pdf_path=f"{rag_path}{policy_number.replace("/", "-")}.pdf")
    return resp


@tool
def check_if_the_damage_cost_does_not_exceed_authorised_repair_limit(cost_of_damage: Annotated[str, "invoice total cost of the damage"],
                                                 policy_number: Annotated[str, "claimant's policy number."]):
    """
    Check if the cost of damage has not exceeded the authorised repair limit covered in the policy.
    """
    # Retrieve
    query = f"\n the cost of the damage is {cost_of_damage}, confirm if the authorised repair limit has not been exceeded in the policy."
    resp = process_query(query=query,pdf_path=f"{rag_path}{policy_number.replace("/", "-")}.pdf")
    return resp

@tool
def check_if_the_premium_page_covers_damage_cost(cost_of_damage: Annotated[str, "invoice total cost of the damage"],
                                                 policy_number: Annotated[str, "claimant's policy number."]):
    """
    Check if the premium paid covers the specified cost of damage in the policy.
    """
    # Retrieve
    query = f"\n the cost of the damage is {cost_of_damage}, confirm if the premium paid covers this cost in the policy."
    resp = process_query(query=query,pdf_path=f"{rag_path}{policy_number.replace("/", "-")}.pdf")
    return resp
