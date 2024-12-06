from src.ai.resources.db_ops import get_claim_from_database
from src.ai.model import init_vertexai
from src.ai.claims_processing.manager import process_message
from src.ai.claims_processing.stirring_agent import super_graph
from src.ai.claims_processing.teams.document_processing.agents import document_check_graph
from src.ai.claims_processing.teams.policy_review.agents import policy_review_graph
from src.ai.claims_processing.teams.fraud_detection.agents import fraud_detection_graph
from langchain_core.messages import HumanMessage

init_vertexai()
# if __name__ == "__main__":
#     process_message(b'83')

# claim_data = {
#     "id": 67,
#     "nameOfInsured": "Ayo Samuel",
#     "policyNumber": "ZG/P/1000/010101/22/000346",
#     "addressOfInsured": "53/55 Omotola street, Alora street",
#     "phoneNumberOfInsured": "not provided",
#     "declaration": True,
#     "signature": "Ayo",
#     "signatureDate": "2024-11-19",
#     "extentOfLossOrDamage": [[]],
#     "particularsAddress": "not provided",
#     "particularsPhoneNo": "not provided",
#     "personInCharge": "Ayo",
#     "addressOfPersonInCharge": "53/55 omotola street, alora street",
#     "permissionConfirmation": "Yes",
#     "otherInsuranceConfirmation": "No",
#     "purposeOfUse": "Personal use",
#     "durationOfOwnership": "2 years",
#     "previousOwner": "SKymit motors",
#     "servicedBy": "A+ mechanics",
#     "lastServiceDate": "2024-12-19",
#     "totalMileage": "1234987",
#     "vehicleMake": "Hyundai",
#     "claimType": "Accident",
#     "registrationNumber": "LND 242 JC",
#     "claimantName": "Ayo Samuel",
#     "vehicleCC": "not provided",
#     "vehicleColor": "Blue",
#     "typeOfBody": "SUV",
#     "yearOfManufacture": "2019",
#     "chassisNumber": "KMD4567483993JJ",
#     "engineNumber": "not provided",
#     "locationAtTimeOfTheft": "not provided",
#     "dateOfDiscovery": None,
#     "discoveredBy": "not provided",
#     "howTheftOccurred": "not provided",
#     "vehicleLicenseNumber": "not provided",
#     "dateReported": None,
#     "policeStationName": "not provided",
#     "wasVehicleLocked": "not provided",
#     "wasNightWatchmanInAttendance": "not provided",
#     "suspect": "not provided",
#     "suspectDetails": "not provided",
#     "resourceUrls": [],
# }
data = get_claim_from_database({'claim_id':85})
print(data)
data.pop('user', None)
data.pop('updatedAt', None)
data.pop('deletedAt', None)
data.pop('createdAt', None)
data.pop('claimReport', None)

print(data)
for s in document_check_graph.stream(
    {
        "messages": [
            HumanMessage(
                content=f"begin this claim processing:\n{data}\n. YOU MUST USE THE SUMMARY TEAM TO PRESENT THE RESULT OF THIS TASK."
            )
        ]
    }
):
    if "__end__" not in s:
        # Extract content values from the dictionary
        for key, value in s.items():
            print(key)
            print()
            if isinstance(value, dict) and "agent_history" in value:
                for message in value["agent_history"]:
                    print(message.content)
            elif isinstance(value, dict) and "messages" in value:
                for message in value["messages"]:
                    print(message.content)

