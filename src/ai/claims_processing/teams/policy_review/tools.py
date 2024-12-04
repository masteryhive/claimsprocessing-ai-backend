from datetime import datetime
from typing import Annotated
from langchain_core.tools import tool

from src.ai.rag.context_stuffing import process_query
from src.ai.rag.retriever import retrieve_from_bigquery
from src.ai.rag.generate_embedding import bq_store
from src.utilities.helpers import _new_get_datetime


@tool
def check_if_claim_is_within_insurance_period():
    """
    Check if the current date falls within the specified insurance period.
    """
    # Retrieve

    query = f"confirm that the insured period is still active."
    resp = process_query(query=query)
    print(resp)
    return resp

@tool
def check_if_claim_is_reported_within_insurance_period(date_of_incident: Annotated[str, "date the incident occured"]):
    """
    Check if the claim is reported within the stipulated notification period.
    """
    # Retrieve
    query = f"\n the date the incident occured is {_new_get_datetime(date_of_incident)}. confirm that the claim is within the stipulated notification period."
    resp = process_query(query=query)
    print(resp)
    return resp

@tool
def check_geographical_coverage(location_of_incident: Annotated[str, "location where the incident occurred"]):
    """
    Check if the incident occurred within the geographical area covered by the policy.
    """
    # Retrieve
    query = f"\n the incident occurred in {location_of_incident}. confirm if the incident occurred within the geographical area covered by the policy."
    resp = process_query(query=query)
    print(resp)
    return resp

@tool
def provide_policy_details():
    """
    Provide all essential details, including terms, policy status, and coverage plan or status.
    """
    # Retrieve
    query = "provide all the crucial information that make up, include terms, policy status and coverage plan/status"
    resp = process_query(query=query)
    print(resp)
    return resp


@tool
def check_premium_coverage(cost_of_damage: Annotated[str, "total cost of the damage"]):
    """
    Check if the premium paid covers the specified cost of damage in the policy.
    """
    # Retrieve
    query = f"\n the cost of the damage is {cost_of_damage}, confirm if the premium paid covers this cost in the policy."
    resp = process_query(query=query)
    print(resp)
    return resp
