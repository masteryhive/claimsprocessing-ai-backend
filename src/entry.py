from src.ai.model import init_vertexai
from src.ai.claims_processing.manager import process_message
from src.ai.claims_processing.stirring_agent import super_graph
from langchain_core.messages import HumanMessage

init_vertexai()
# if __name__ == "__main__":
#     process_message(b'67')

claim_data = {
    "id": 67,
    "nameOfInsured": "Ayo Samuel",
    "policyNumber": "ZG/P/1000/010101/22/000346",
    "addressOfInsured": "53/55 Omotola street, Alora street",
    "phoneNumberOfInsured": "not provided",
    "declaration": True,
    "signature": "Ayo",
    "signatureDate": "2024-11-19",
    "extentOfLossOrDamage": [[]],
    "particularsAddress": "not provided",
    "particularsPhoneNo": "not provided",
    "personInCharge": "Ayo",
    "addressOfPersonInCharge": "53/55 omotola street, alora street",
    "permissionConfirmation": "Yes",
    "otherInsuranceConfirmation": "No",
    "purposeOfUse": "Personal use",
    "durationOfOwnership": "2 years",
    "previousOwner": "SKymit motors",
    "servicedBy": "A+ mechanics",
    "lastServiceDate": "2024-12-19",
    "totalMileage": "1234987",
    "vehicleMake": "Hyundai",
    "claimType": "Accident",
    "registrationNumber": "LND 242 JC",
    "claimantName": "Ayo Samuel",
    "vehicleCC": "not provided",
    "vehicleColor": "Blue",
    "typeOfBody": "SUV",
    "yearOfManufacture": "2019",
    "chassisNumber": "KMD4567483993JJ",
    "engineNumber": "not provided",
    "locationAtTimeOfTheft": "not provided",
    "dateOfDiscovery": None,
    "discoveredBy": "not provided",
    "howTheftOccurred": "not provided",
    "vehicleLicenseNumber": "not provided",
    "dateReported": None,
    "policeStationName": "not provided",
    "wasVehicleLocked": "not provided",
    "wasNightWatchmanInAttendance": "not provided",
    "suspect": "not provided",
    "suspectDetails": "not provided",
    "resourceUrls": [],
}

for s in super_graph.stream(
    {
        "messages": [
            HumanMessage(
                content=f"begin this claim processing:\n{claim_data}\n. YOU MUST USE THE SUMMARY TEAM TO PRESENT THE RESULT OF THIS TASK."
            )
        ]
    }
):
    if "__end__" not in s:
        print(s)
