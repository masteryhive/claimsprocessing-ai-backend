import asyncio
import json
# from src.parsersfraud_team_parser import extract_from_fraud_checks
from src.teams.resources.document_understanding import classify_supporting_documents
from src.models.claim_processing import AccidentClaimData, TheftClaimData
from src.database.db_ops import get_claim_from_database
from src.ai_models.model import init_vertexai
from src.workflow_orch.manager import process_message
# from ai.claims_processing.stirring_agent import super_graph
# from ai.claims_processing.teams.document_processing.agents import (
#     document_check_graph,
# )
# from src.parserssettlement_team_parser import extract_from_settlement_offer
# from config.db_setup import SessionLocal
# from src.teams.policy_review.agents import policy_review_graph
from src.teams.fraud_detection.agents import fraud_detection_graph
# from src.teams.settlement_offer.agents import settlement_offer_graph
from langchain_core.messages import HumanMessage
from src.utilities.helpers import _new_get_datetime

init_vertexai()
# if __name__ == "__main__":
#     # delete_claim_report_by_id(SessionLocal(),90)
#     process_message(b"90")


# {
#     "id": 85,
#     "nameOfInsured": "Ayo Samuel",8
#     "policyNumber": "ZG/P/1000/010101/22/000346",
#     "addressOfInsured": "plot 23, colegeorge estate, college road, ogba Ikeja",
#     "phoneNumberOfInsured": "+2348012675443",
#     "declaration": True,
#     "signature": "Ayo Samuel",
#     "status": "Examining claim form",
#     "signatureDate": "2024-12-19",
#     "extentOfLossOrDamage": [
#         {"item": "Driver side mirror", "costPrice": 1200000, "amountClaimed": 700000},
#         {
#             "item": "Partial Paint Job (oven baked)",
#             "costPrice": 80000,
#             "amountClaimed": 600000,
#         },
#         {"item": "Driver side door handle", "costPrice": 90000, "amountClaimed": 90000},
#     ],
#     "particularsAddress": "not provided",
#     "particularsPhoneNo": "not provided",
#     "personInCharge": "Ayo Samuel",
#     "addressOfPersonInCharge": "plot 23, colegeorge estate, college road, ogba Ikeja",
#     "permissionConfirmation": "Yes",
#     "otherInsuranceConfirmation": "No",
#     "purposeOfUse": "Personal use",
#     "durationOfOwnership": "2 years",
#     "previousOwner": "SKymit motors",
#     "servicedBy": "A+ mechanics",
#     "lastServiceDate": "2024-12-19",
#     "totalMileage": "1001043",
#     "vehicleMake": "Hyundai",
#     "claimType": "accident",
#     "registrationNumber": "LND 242 JC",
#     "claimantName": "Ayo Samuel",
#     "vehicleCC": "not provided",
#     "vehicleColor": "Blue",
#     "typeOfBody": "SUV",
#     "yearOfManufacture": "2019",
#     "chassisNumber": "KMD4567483993JJ",
#     "engineNumber": "not provided",
#     "locationAtTimeOfTheft": "I was in traffic",
#     "dateOfDiscovery": None,
#     "discoveredBy": "I discovered the damage myself",
#     "howTheftOccurred": "None",
#     "vehicleLicenseNumber": "N/A",
#     "dateReported": None,
#     "policeStationName": "I have not been to the police station",
#     "wasVehicleLocked": "yes",
#     "wasNightWatchmanInAttendance": "N/A",
#     "suspect": "No",
#     "suspectDetails": "not provided",
#     "roomId": "14029f61-85c1-4582-be4f-6e9aa1683350",
#     "dateClaimFiled": "2024-12-06T00:56:09.381Z",
#     "evidenceProvided": ["This image presents compelling visual documentation of damage to a vehicle, specifically a blue car, and can therefore serve as valid evidence for a vehicle insurance claim.  The photograph clearly shows substantial damage to the driver's side.  The driver's side door exhibits significant deformation and denting, suggesting a forceful impact.  The side mirror is also damaged and appears to be partially detached from the vehicle.  The front fender, adjacent to the driver's side door, also displays noticeable crumpling and damage.  This collection of damage points to a collision or impact event affecting the front left quadrant of the car.  The extent of the damage visible in the image warrants an insurance claim.\n", 'This document is an **invoice** from Timothy Auto Shop. It likely serves as evidence for a vehicle insurance claim for repairs necessitated by an incident that damaged the driver\'s side and trunk of the vehicle.\n\n**Items:**\n\n* **Partial oven baked painting for the driver side to the trunk (Labour):** ₦32,000 (4 x ₦8,000)\n* **Parts:** ₦265,000 (Not itemized)\n\n**Total Price:**\n\n* **Total:** ₦300,000\n\n**Narration:**\n\nThere isn\'t a specific descriptive narration beyond the item description "Partial oven baked painting for the driver side to the trunk."  This indicates the repair work performed.\n\n**Purpose:**\n\nThe purpose of this invoice is to bill the customer (or their insurance company) for the repairs completed on their vehicle. It serves as a record of the services provided, the costs associated with those services, and the payment terms.  In the context of an insurance claim, it provides evidence of the cost of repairs to justify the claim amount.\n'],
# }


# claim_data = {
#     "nameOfInsured": "Olalekan Adisa",
#     "policyNumber": "0000980404",
#     "addressOfInsured": "53/55 Omotola street, Aguda Surulere",
#     "phoneNumberOfInsured": "09016827203",
#     "declaration": True,
#     "extentOfLossOrDamage": [
#         {
#             "item": "Driver side mirror",
#             "costPrice": 40000,
#             "amountClaimed": 40000
#         }
#     ],
#     "personInCharge": "Olalekan Adisa",
#     "addressOfPersonInCharge": "53/55 Adetola Street Aguda Surulere",
#     "permissionConfirmation": "Yes",
#     "otherInsuranceConfirmation": "No",
#     "purposeOfUse": "Personal use",
#     "durationOfOwnership": "2 years",
#     "incidentDetails": "The claimant reported that while driving to work, a reckless driver hit their car by the side, breaking the side mirror.",
#     "previousOwner": "SKymit motors",
#     "servicedBy": "A+ mechanics",
#     "lastServiceDate": "2024-12-19",
#     "totalMileage": "67000",
#     "vehicleMake": "Hyundai",
#     "claimType": "accident",
#     "registrationNumber": "KSF 727 HB",
#     "claimantName": "Olalekan Adisa",
#     "vehicleColor": "Black",
#     "typeOfBody": "Sonata",
#     "yearOfManufacture": "2014",
#     "chassisNumber": "5NPE34AF1FH095171",
#     "engineNumber": "not provided",
#     "vehicleLicenseNumber": "KSF 727 HB",
#     "policeStationName": "not provided",
#     "evidenceProvided": [
#         "The image depicts significant damage to the driver's side exterior mirror of a vehicle.  The damage is extensive, showing the mirror's internal components completely exposed.  The outer casing of the mirror appears intact, but the internal mechanisms, including the wiring harness and indicator light assembly, are severely damaged and displaced from their normal positions.  The internal structure of the mirror housing is broken, indicating a forceful impact. The level of damage suggests the mirror is non-functional.  While the image quality is sufficient to ascertain the extent of the damage, the precise nature of the impact which caused the damage cannot be determined from the image alone.  The claimant should review the image and verify that the displayed damage accurately reflects the extent of their loss.\n - evidenceSourceUrl: https://storage.googleapis.com/masteryhive-insurance-claims/rawtest/Scenario1/20211001_164221.jpg",
#         "- Invoice Information:\n  * Invoice Number: 0050\n  * Date: 30th Nov 2024\n  * Customer Name: Olalekan Adisa\n  * Customer Address: 53/55 Omotola street, Alora street, Lagos, Nigeria\n  * Vehicle Make/Model: Hyundai/Sonata\n  * Vehicle Registration Number: KSF 727 HB\n\n- Items and Cost:\n  * Driver side mirror: 1 x ₦40,000 = ₦40,000\n  * Labour Cost: 4hrs x ₦2,500 = ₦10,000\n\n- Total Cost:\n  * Total Amount Due: ₦50,000\n\n- Invoice Narration and Purpose: This invoice details the cost of repair for the driver side mirror of a Hyundai Sonata with registration number KSF 727 HB. The cost includes the price of a new driver side mirror and the labour cost for its repair.\n - evidenceSourceUrl: https://storage.googleapis.com/masteryhive-insurance-claims/rawtest/Scenario1/Auto_Shop_Invoice.pdf"
#     ],
#     "ssim": {
#         "prelossUrl": "https://storage.googleapis.com/masteryhive-insurance-claims/rawtest/preloss/preloss_0000980404.jpg",
#         "claimUrl": "https://storage.googleapis.com/masteryhive-insurance-claims/rawtest/Scenario1/20211001_164221.jpg"
#     },
#     "dateClaimFiled": "December 15 2024",
#     "repairInvoice": "- Invoice Information:\n  * Invoice Number: 0050\n  * Date: 30th Nov 2024\n  * Customer Name: Olalekan Adisa\n  * Customer Address: 53/55 Omotola street, Alora street, Lagos, Nigeria\n  * Vehicle Make/Model: Hyundai/Sonata\n  * Vehicle Registration Number: KSF 727 HB\n\n- Items and Cost:\n  * Driver side mirror: 1 x ₦40,000 = ₦40,000\n  * Labour Cost: 4hrs x ₦2,500 = ₦10,000\n\n- Total Cost:\n  * Total Amount Due: ₦50,000\n\n- Invoice Narration and Purpose: This invoice details the cost of repair for the driver side mirror of a Hyundai Sonata with registration number KSF 727 HB. The cost includes the price of a new driver side mirror and the labour cost for its repair.\n"
# }


if __name__ == "__main__":
    # delete_claim_report_by_id(SessionLocal(),91)
    claim_data = get_claim_from_database("96")
    # print(claim_data)
    print()
    claim_data['dateClaimFiled'] = _new_get_datetime(claim_data["createdAt"])
    if len(claim_data['resourceUrls']) != 0:
        print(claim_data['resourceUrls'])
        print()
        result = asyncio.run(classify_supporting_documents(claim_data))
        claim_data = result
    if claim_data["claimType"] in ["Accident","accident"]:
        claim_data = AccidentClaimData(**claim_data)
    else:
        claim_data = TheftClaimData(**claim_data)

    # print(claim_data)
    for s in fraud_detection_graph.stream(
        {"messages": [HumanMessage(content=(
                            "Important information:"
                            "\nThis service is currently run in Nigeria, this means:"
                            "\n1. The currency is \u20a6"
                            f"\n\nBegin this claim processing using this claim form JSON data:\n {claim_data.model_dump()}"
                            "\n\nYOU MUST USE THE SUMMARY TEAM TO PRESENT THE RESULT OF THIS TASK."
                        ))],
        #  "claim_form_json":[HumanMessage(
        #                 content=json.dumps(claim_data.model_dump()))]
                        }
    ):
        if "__end__" not in s:
            # Extract content values from the dictionary
            for key, value in s.items():
                if isinstance(value, dict) and "agent_history" in value:
                    for message in value["agent_history"]:
                        print(message.content)
                elif isinstance(value, dict) and "messages" in value:
                    for message in value["messages"]:
                        print(message.content)
                        # print(extract_from_fraud_checks(message.content))
