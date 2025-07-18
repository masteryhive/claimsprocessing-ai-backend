import json
from typing import Annotated
from langchain_core.tools import tool
from src.rag.context_stuffing import process_query
from src.teams.policy_review.helper import check_claim_notification_period
from src.utilities.helpers import _new_get_datetime
from datetime import datetime

from pathlib import Path

from src.utilities.pdf_handlers import download_pdf

rag_path = Path(__file__).parent.parent / "policy_doc/"


@tool
def retrieve_all_essential_details_from_policy(
    policyNumber: Annotated[str, "claimant's policy number."]
):
    """
    Use this tool to retrieve all essential details, including terms, policy status, and coverage plan or status.
    """
    download_pdf(policyNumber, rag_path)
    # Retrieve
    query = "Please, analyze this vehicle insurance policy document comprehensively and provide all critical information in a template format.\nThe current date(YYYY-MM-DD) is {current_date}."

    response_schema = {
        "type": "object",
        "properties": {
            "PolicyBasics": {
                "type": "object",
                "properties": {
                    "PolicyPeriod": {
                        "type": "object",
                        "properties": {
                            "From": {
                                "type": "string",
                                "description": "The start date of the policy period, typically found in sections labeled 'policy period' or 'coverage dates'.",
                            },
                            "To": {
                                "type": "string",
                                "description": "The end date of the policy period, typically found in sections labeled 'policy period' or 'coverage dates'.",
                            },
                        },
                    },
                    "PolicyType": {
                        "type": "string",
                        "description": "Type of policy and coverage category (e.g., 'comprehensive', 'third-party').",
                    },
                    "PremiumDetails": {
                        "type": "object",
                        "properties": {
                            "AnnualPremium": {
                                "type": "string",
                                "description": "The annual premium amount, from terms such as 'yearly cost' or 'premium amount'.",
                            },
                            "PaidAmount": {
                                "type": "string",
                                "description": "The amount already paid, sometimes labeled as 'installments paid'.",
                            },
                            "PaymentTerms": {
                                "type": "string",
                                "description": "Payment terms such as 'monthly', 'quarterly', or 'annually'.",
                            },
                        },
                    },
                    "PolicyholderDetails": {
                        "type": "string",
                        "description": "Details about the policyholder, from fields like 'insured name', 'customer info', etc.",
                    },
                },
            },
            "VehicleDetails": {
                "type": "object",
                "properties": {
                    "MakeModelYear": {
                        "type": "string",
                        "description": "Vehicle make, model, and year, identified by terms like 'vehicle description'.",
                    },
                    "ValueInsured": {
                        "type": "string",
                        "description": "Vehicle value or sum insured, referred to as 'coverage amount' or 'asset value'.",
                    },
                    "UsageType": {
                        "type": "string",
                        "description": "Vehicle usage type, such as 'personal', 'private', or 'commercial'.",
                    },
                },
            },
            "CoverageDetails": {
                "type": "object",
                "properties": {
                    "MainCoverageTypes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of primary coverage types, including 'basic coverage' or 'default protection'.",
                    },
                    "AdditionalCoverages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional coverages or riders, referenced as 'addons' or 'enhancements'.",
                    },
                    "CoverageLimits": {
                        "type": "string",
                        "description": "Coverage limits and sub-limits, found under terms like 'maximum payout' or 'policy limit'.",
                    },
                    "RepairLimits": {
                        "type": "string",
                        "description": "Authorized repair limits, sometimes labeled 'repair cap'.",
                    },
                },
            },
            "KeyTermsConditions": {
                "type": "object",
                "properties": {
                    "Conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "All terms and conditions, found under 'policy stipulations' or 'requirements'.",
                    },
                    "Warranties": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Warranty information, also termed 'guarantees'.",
                    },
                    "SpecialClauses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Special clauses or provisions.",
                    },
                    "Endorsements": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Endorsements, sometimes referred to as 'amendments' or 'policy notes'.",
                    },
                },
            },
            "ExclusionsLimitations": {
                "type": "object",
                "properties": {
                    "Exclusions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of exclusions, also called 'policy restrictions' or 'non-covered items'.",
                    },
                    "GeographicLimits": {
                        "type": "string",
                        "description": "Geographic limitations, often labeled as 'service area' or 'coverage region'.",
                    },
                    "UsageRestrictions": {
                        "type": "string",
                        "description": "Restrictions on usage, referenced as 'limitations of use'.",
                    },
                },
            },
            "ClaimsRequirements": {
                "type": "object",
                "properties": {
                    "Procedure": {
                        "type": "string",
                        "description": "The claims procedure, found as 'filing process' or 'claim handling'.",
                    },
                    "NotificationPeriod": {
                        "type": "string",
                        "description": "Required notification period for claims, labeled as 'reporting time'.",
                    },
                    "DocumentsRequired": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of required documentation for claims.",
                    },
                    "ContactNumbers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Emergency contact numbers.",
                    },
                    "NoClaimBonus": {
                        "type": "string",
                        "description": "Details about no-claim bonus, found under 'reward for no claims'.",
                    },
                    "SubmissionTimeLimit": {
                        "type": "string",
                        "description": "Time limits for submitting claims.",
                    },
                    "AccidentReporting": {
                        "type": "string",
                        "description": "Accident or incident reporting requirements.",
                    },
                },
            },
            "CancellationModification": {
                "type": "object",
                "properties": {
                    "CancellationTerms": {
                        "type": "string",
                        "description": "Terms for policy cancellation, labeled as 'termination rules'.",
                    },
                    "ModificationProcedure": {
                        "type": "string",
                        "description": "Policy modification procedures.",
                    },
                    "RefundPolicy": {
                        "type": "string",
                        "description": "Refund conditions for cancellations.",
                    },
                },
            },
        },
        "required": [
            "PolicyBasics",
            "VehicleDetails",
            "CoverageDetails",
            "KeyTermsConditions",
            "ExclusionsLimitations",
            "ClaimsRequirements",
            "CancellationModification",
        ],
    }

    resp = process_query(
        prompt=query,
        pdf_path=f"{rag_path}/{policyNumber.replace("/", "-")}.pdf",
        response_schema=response_schema,
    )
    return resp


@tool
def check_if_this_claim_is_within_insurance_period(
    policyNumber: Annotated[str, "claimant's policy number."]
):
    """
    Check if the current date falls within the specified insurance period.
    """
    download_pdf(policyNumber, rag_path)
    response_schema = {
        "type": "object",
        "properties": {
            "InsurancePeriod": {
                "type": "object",
                "properties": {
                    "StartDate": {
                        "type": "string",
                        "description": "The start date of the insurance period.",
                    },
                    "EndDate": {
                        "type": "string",
                        "description": "The end date of the insurance period.",
                    },
                    "IsActive": {
                        "type": "boolean",
                        "description": "Indicates if the insurance policy is currently active.",
                    },
                },
                "required": ["StartDate", "EndDate", "IsActive"],
            }
        },
        "required": ["InsurancePeriod"],
    }

    # Ensure the current date is correctly formatted and retrieved
    current_date = datetime.now().date()  # Get the current date
    query = f"Please, confirm that the insured period is still active.\nThe current date(YYYY-MM-DD) is {current_date}."
    
    resp = process_query(
        prompt=query,
        pdf_path=f"{rag_path}/{policyNumber.replace('/', '-')}.pdf",
        response_schema=response_schema,
    )
    
    # Load the response and check the active status
    insurance_period_data = json.loads(resp)["InsurancePeriod"]
    start_date = datetime.strptime(insurance_period_data["StartDate"], "%Y-%m-%d").date()
    end_date = datetime.strptime(insurance_period_data["EndDate"], "%Y-%m-%d").date()

    # Check if the current date falls within the policy period
    is_active = start_date <= current_date <= end_date

    return {"IsActive": is_active}


@tool
def check_if_this_claim_adhered_to_notification_period(
    policyNumber: Annotated[str, "claimant's policy number."],
    claim_reporting_date: Annotated[str, "the claim reporting date."]
):
    """
    Check if the claim was reported within the stipulated notification period.
    """
    download_pdf(policyNumber, rag_path)
    response_schema = {
        "type": "object",
        "properties": {
            "ClaimNotification": {
                "type": "object",
                "properties": {
                    "NotificationPeriod": {
                        "type": "number",
                        "description": "The allowed period for claim notification as per the policy.",
                    },
                },
                "required": ["NotificationPeriod"],
            }
        },
        "required": ["ClaimNotification"],
    }

    query = (
        f"\n the date the incident occured is {_new_get_datetime(claim_reporting_date)}.",
        " Please, confirm that the claim is within the stipulated notification period.",
        "The current date(YYYY-MM-DD) is {current_date}.",
    )
    resp = process_query(
        prompt="".join(query),
        pdf_path=f"{rag_path}/{policyNumber.replace("/", "-")}.pdf",
        response_schema=response_schema,
    )
    notificationPeriod = json.loads(resp)["ClaimNotification"]["NotificationPeriod"]
    result = check_claim_notification_period(claim_reporting_date, int(notificationPeriod))
    return result



# @tool
# def check_if_the_damage_cost_does_not_exceed_authorised_repair_limit(
#     cost_of_damage: Annotated[str, "invoice total cost of the damage"],
#     policyNumber: Annotated[str, "claimant's policy number."],
# ):
#     """
#     Check if the cost of damage has not exceeded the authorised repair limit covered in the policy.
#     """
#     download_pdf(policyNumber, rag_path)
#     response_schema = {
#         "type": "object",
#         "properties": {
#             "RepairLimit": {
#                 "type": "object",
#                 "properties": {
#                     "AuthorisedLimit": {
#                         "type": "number",
#                         "description": "The authorised repair limit as specified in the policy.",
#                     },
#                     "IsWithinLimit": {
#                         "type": "boolean",
#                         "description": "Indicates if the cost of damage is within the authorised repair limit.",
#                     },
#                 },
#                 "required": ["AuthorisedLimit", "IsWithinLimit"],
#             }
#         },
#         "required": ["RepairLimit"],
#     }

#     query = (
#         f"\n the cost of the damage is {cost_of_damage}.",
#         "Please, confirm if the authorised repair limit has not been exceeded in the policy.",
#         "\nThe current date(YYYY-MM-DD) is {current_date}.",
#     )
#     resp = process_query(
#         prompt=query,
#         pdf_path=f"{rag_path}/{policyNumber.replace("/", "-")}.pdf",
#         response_schema=response_schema,
#     )
#     return resp

# @tool
# def check_if_the_incident_occurred_within_the_geographical_coverage(
#     location_of_incident: Annotated[
#         str, "location where the incident occurred, default is Lagos, Nigeria"
#     ],
#     policyNumber: Annotated[str, "claimant's policy number."],
# ):
#     """
#     Check if the incident occurred within the geographical area covered by the policy.
#     """
#     download_pdf(policyNumber, rag_path)
#     response_schema = {
#         "type": "object",
#         "properties": {
#             "GeographicalCoverage": {
#                 "type": "object",
#                 "properties": {
#                     "CoveredArea": {
#                         "type": "string",
#                         "description": "The geographical area covered by the policy.",
#                     },
#                     "IsWithinCoverage": {
#                         "type": "boolean",
#                         "description": "Indicates if the incident location is within the geographical coverage area.",
#                     },
#                 },
#                 "required": ["CoveredArea", "IsWithinCoverage"],
#             }
#         },
#         "required": ["GeographicalCoverage"],
#     }

#     query = "\n the incident occurred in Lagos, Nigeria. confirm if the incident occurred within the geographical area covered by the policy.\nThe current date(YYYY-MM-DD) is {current_date}."
#     resp = process_query(
#         prompt=query,
#         pdf_path=f"{rag_path}/{policyNumber.replace("/", "-")}.pdf",
#         response_schema=response_schema,
#     )
#     print(resp)
#     return resp


# @tool
# def check_if_the_premium_page_covers_damage_cost(
#     cost_of_damage: Annotated[str, "invoice total cost of the damage"],
#     policyNumber: Annotated[str, "claimant's policy number."],
# ):
#     """
#     Check if the premium paid covers the specified cost of damage in the policy.
#     """
#     download_pdf(policyNumber, rag_path)
#     response_schema = {
#         "type": "object",
#         "properties": {
#             "PremiumCoverage": {
#                 "type": "object",
#                 "properties": {
#                     "TotalPremiumPaid": {
#                         "type": "number",
#                         "description": "The total premium amount paid as specified in the policy.",
#                     },
#                     "CoversDamageCost": {
#                         "type": "boolean",
#                         "description": "Indicates if the premium paid covers the specified cost of damage.",
#                     },
#                 },
#                 "required": ["TotalPremiumPaid", "CoversDamageCost"],
#             }
#         },
#         "required": ["PremiumCoverage"],
#     }

#     query = (
#         f"The cost of the damage is {cost_of_damage}.",
#         " confirm if the premium paid covers this cost in the policy.",
#         "\nThe current date(YYYY-MM-DD) is {current_date}.",
#     )
#     resp = process_query(
#         prompt=query,
#         pdf_path=f"{rag_path}/{policyNumber.replace("/", "-")}.pdf",
#         response_schema=response_schema,
#     )
#     print(resp)
#     return resp
