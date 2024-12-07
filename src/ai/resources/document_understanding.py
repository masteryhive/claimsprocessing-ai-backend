# import libraries
import asyncio
import aiohttp
import os, httpx, base64, io, fitz, uuid
from langchain_google_vertexai import ChatVertexAI
from PIL import Image
from src.ai.resources.image_understanding import claims_image_evidence_recognizer
from src.ai.llm import llm


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
    response = llm.invoke([message])
    return response.content


def document_understanding(doc_url: str) -> str:
    temp_file = download_pdf(pdf_url=doc_url)
    base64_image = pdf_page_to_base64(temp_file, 2)
    prompt = (
        "Identify what this document is, it is meant to serve as evidence for an vehicle insurance claim. Extract relevant information from it like invoice total cost and items, invoice narration and purpose."
        "- List all items mentioned in the invoice along with their individual prices. "
        "- Calculate and provide the total price for all items. "
        "- Extract the invoice narration, if available, and specify its purpose. "
        "Ensure your response is structured clearly with separate sections for items, total price, narration, and purpose."
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
    response = llm.invoke([message])
    return response.content



async def fetch_content_type(session, url):
    """Fetch the content type of a given URL."""
    try:
        async with session.head(url, timeout=10) as response:
            content_type = response.headers.get("Content-Type", "")
            return url, content_type
    except Exception as e:
        return url, f"Error: {e}"

async def classify_urls(resource_dict):
    """Classify URLs as PDFs or images based on content type."""
    supporting_documents = []
    images = []
    others = []

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in resource_dict["resourceUrls"]:
            tasks.append(fetch_content_type(session, url))
        
        results = await asyncio.gather(*tasks)
        
        for url, content_type in results:
            if "application/pdf" in content_type:
                supporting_documents.append(document_understanding(url))
            elif "image/" in content_type:
                supporting_documents.append(await claims_image_evidence_recognizer(url))
            else:
                others.append(url)

    return supporting_documents