# import libraries
import asyncio
from io import BytesIO
import httpx, base64
from src.ai_models.llm import llm_flash as llm

from PIL import Image
from vertexai.preview.generative_models import (
    GenerationResponse,
    GenerativeModel,
       GenerationConfig,
    HarmBlockThreshold,
    HarmCategory,
    Part
)

# function to fetch image
async def fetch_image(image_url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url, timeout=300)
        response.raise_for_status()  # Raise exception if the request failed
    return response.content

async def convert_image_to_format(image_bytes: bytes, output_format: str) -> bytes:
    """
    Converts the image bytes into the desired format ('jpeg' or 'png').

    :param image_bytes: Bytes of the original image.
    :param output_format: Target format ('jpeg' or 'png').
    :return: Bytes of the converted image in the specified format.
    """
    with Image.open(BytesIO(image_bytes)) as img:
        if output_format.lower() == "jpeg":
            img = img.convert("RGB")  # Ensure no transparency for JPEG
        output_buffer = BytesIO()
        img.save(output_buffer, format=output_format.upper())
        output_buffer.seek(0)
        return output_buffer.read()

async def process_image(image_url: str, output_format: str = "jpeg") -> str:
    """
    Fetches an image from the URL and converts it to the specified format.

    :param image_url: URL of the image to fetch.
    :param output_format: Target format ('jpeg' or 'png').
    :return: Base64-encoded string of the converted image.
    """
    image_bytes = await fetch_image(image_url)
    converted_image = await convert_image_to_format(image_bytes, output_format)
    return base64.b64encode(converted_image).decode("utf-8")

async def claims_image_evidence_recognizer(image_url: str) -> str:
    base64_image = await process_image(image_url=image_url)
    prompt = ("Identify what is in this image meant to serve as evidence for an vehicle insurance claim. "
"If it is related to a car, respond with which part(s) of the car appears damaged."
"if it is not respond with 'not a valid image evidence for claims'."
"Always provide your response as highly verbose as possible"
"                                                       "
"**Additional Notes:**"
"                     "
"* **Clarity and Detail:** Be as specific as possible when describing the damage."
"* **Image Quality:** If the image quality is too poor to assess the damage or extract information, indicate this in the output."
"* **Human Intervention:** For complex or ambiguous cases, indicate this in the output. suggest that the claimant review the image for further verification.")
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
