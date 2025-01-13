# import libraries
import asyncio
import aiohttp
import os, httpx, base64, io, fitz, uuid
from langchain_google_vertexai import ChatVertexAI
from PIL import Image
from teams.resources.helpers import get_preloss
from teams.resources.image_understanding import claims_image_evidence_recognizer
from ai_models.llm import llm_flash


def download_pdf(
    pdf_url: str, temp_folder: str = "temp", filename: str = str(uuid.uuid4())
) -> str:
    # Define the path to save the PDF file temporarily
    os.makedirs(temp_folder, exist_ok=True)
    tempFile = os.path.join(temp_folder, filename)

    # Download the PDF file
    with httpx.stream("GET", pdf_url, timeout=300) as response:
        response.raise_for_status()
        with open(tempFile, "wb") as pdf_file:
            for chunk in response.iter_bytes():
                pdf_file.write(chunk)

    return tempFile


def pdf_page_to_base64(pdf_path: str, page_number: int):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(page_number - 1)  # input is one-indexed
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def claims_form_recognizer(doc_url: str) -> str:
    temp_file = download_pdf(pdf_url=doc_url)
    base64_image = pdf_page_to_base64(temp_file, 2)
    prompt = """Identify if this document is a motor insurance claims form.
If it is, extract the following fields and the data filled in from the document as key,value pairs with linebreak e.g {{"policyNumber":"//the data filled in","claimType":"//the claim type filled in"}}:
policyNumber, claimType, nameOfInsured, claimantName, roomId, addressOfInsured, 
phoneNumberOfInsured, declaration, signature, signatureDate, extentOfLossOrDamage, 
particularsAddress, particularsPhoneNo, personInCharge, addressOfPersonInCharge, 
permissionConfirmation, otherInsuranceConfirmation, purposeOfUse, durationOfOwnership, 
previousOwner, servicedBy, lastServiceDate, totalMileage, vehicleMake, registrationNumber, 
vehicleCC, vehicleColor, typeOfBody, yearOfManufacture, chassisNumber, engineNumber, 
locationAtTimeOfTheft, dateOfDiscovery, discoverdBy, howTheftOccurred, vehicleLicenseNumber, 
dateReported, policeStationName, wasVehicleUnlocked, wasNightWatchmanInAttendance, suspect, 
suspectDetails.
if it is not respond with 'not a claim form"""
    from langchain_core.messages import HumanMessage

    # Initialize the model
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ],
    )
    response = llm_flash.invoke([message])
    return response.content


def invoice_entity_extraction(doc_url: str) -> str:
    temp_file = download_pdf(pdf_url=doc_url)
    base64_image = pdf_page_to_base64(temp_file, 1)
    prompt = ("Identify what this document is and extract relevant information from it like invoice total cost and items, invoice narration and purpose."
    "[TEMPLATE]"
    " - Invoice Information:{{the_general_infomation_about_the_invoice_in_bullet_points(-)_(e.g. invoice number, date, customer name, vehicle registration and information etc.)}}"
    " - Items and Cost: {{the_individual_items_and_their_cost_in_bullet_points(-)_(e.g.  - Driver side mirror: 1 x ₦40,000 = ₦40,000\n- Labour Cost: 2.5hrs x ₦2,500 = ₦10,000)}}"
    " - Total Cost: {{the_total_amount_due(-)_(e.g.  - Total Amount Due: ₦50,000)}} <-- item cost(s) plus labour cost -->"
    " - Invoice Narration and Purpose:{{a_narration_of_the_invoice_and_it's_purpose}}"
    )
    from langchain_core.messages import HumanMessage

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ],
    )
    response = llm_flash.invoke([message])
    return response.content


async def fetch_content_type(session, url):
    """Fetch the content type of a given URL."""
    try:
        async with session.head(url, timeout=10) as response:
            content_type = response.headers.get("Content-Type", "")
            return url, content_type
    except Exception as e:
        return url, f"Error: {e}"


async def classify_supporting_documents(resource_dict:dict)->dict:
    """Classify URLs as PDFs or images based on content type."""
    supporting_documents = []
    result = []
    vehicle_url = ""
    invoice_data=""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in resource_dict["resourceUrls"]:
            tasks.append(fetch_content_type(session, url))

        results = await asyncio.gather(*tasks)

        for url, content_type in results:
            if "application/pdf" in content_type:
                invoice_data = invoice_entity_extraction(url)
                supporting_documents.append(f"{invoice_data} - evidenceSourceUrl: {url}")
            elif "image/" in content_type:
                vehicle_url=url
                supporting_documents.append(f"{await claims_image_evidence_recognizer(url)} - evidenceSourceUrl: {url}")
            else:
                result.append(url)
    resource_dict.pop('resourceUrls', None)
    resource_dict["evidenceProvided"] = supporting_documents
    resource_dict["repairInvoice"] = invoice_data
                
    resource_dict["ssim"]  = {
            "prelossUrl":get_preloss(resource_dict["policyNumber"]),
            "claimUrl": vehicle_url
        }
    return resource_dict
