
from typing import Annotated
from langchain_core.tools import tool
from src.ai.rag.context_stuffing import download_pdf, process_query
from src.ai.rag.generate_embedding import bq_store
from src.utilities.helpers import _new_get_datetime


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
    query = "provide all the crucial information that make up, include terms, policy status and coverage plan/status except vehicle license number/registration number. Do not redact any information."
    resp = process_query(query=query,pdf_path=f"src/ai/rag/doc/{policy_number.replace("/", "-")}.pdf")
    return resp


@tool
def check_if_this_claim_is_within_insurance_period(policy_number: Annotated[str, "claimant's policy number."]):
    """
    Check if the current date falls within the specified insurance period.
    """
    # Retrieve

    query = f"confirm that the insured period is still active."
    resp = process_query(query=query,pdf_path=f"src/ai/rag/doc/{policy_number.replace("/", "-")}.pdf")
    return resp

@tool
def check_if_this_claim_is_reported_within_insurance_period(date_of_incident: Annotated[str, "date the incident occured"],
                                                            policy_number: Annotated[str, "claimant's policy number."]):
    """
    Check if the claim is reported within the stipulated notification period.
    """
    # Retrieve
    query = f"\n the date the incident occured is {_new_get_datetime(date_of_incident)}. confirm that the claim is within the stipulated notification period."
    resp = process_query(query=query,pdf_path=f"src/ai/rag/doc/{policy_number.replace("/", "-")}.pdf")
    return resp

@tool
def check_if_the_incident_occurred_within_the_geographical_coverage(location_of_incident: Annotated[str, "location where the incident occurred, default is Lagos, Nigeria"],
                                                                    policy_number: Annotated[str, "claimant's policy number."]):
    """
    Check if the incident occurred within the geographical area covered by the policy.
    """
    # Retrieve
    query = f"\n the incident occurred in Lagos, Nigeria. confirm if the incident occurred within the geographical area covered by the policy."
    resp = process_query(query=query,pdf_path=f"src/ai/rag/doc/{policy_number.replace("/", "-")}.pdf")
    return resp


@tool
def check_if_the_premium_page_covers_damage_cost(cost_of_damage: Annotated[str, "total cost of the damage"]):
    """
    Check if the premium paid covers the specified cost of damage in the policy.
    """
    # Retrieve
    query = f"\n the cost of the damage is {cost_of_damage}, confirm if the premium paid covers this cost in the policy."
    resp = process_query(query=query,pdf_path=f"src/ai/rag/doc/{policy_number.replace("/", "-")}.pdf")
    return resp
