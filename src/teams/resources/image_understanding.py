# import libraries
import asyncio
from io import BytesIO
from typing import Any, Dict, List
import httpx, base64
from ai_models.llm import llm_flash as llm
from src.config.appconfig import env_config
from vertexai.generative_models import GenerativeModel, Part
from PIL import Image

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


########## SSIM with Vertex AI ################

pre_prompt = """
This is the image of the vehicle before loss, used as a reference for comparison.
"""

prompt = """
Objective:
Perform a comprehensive analysis of vehicle images to evaluate pre-existing conditions and detect potential new damages for insurance claim assessment.

Claimant Claim details:
{claim_details}

Image Analysis Protocol:
Compare the "image of the vehicle before loss" with the other provided image(s) and perform the following evaluations:

[TEMPLATE]
1. **Image Similarity Analysis:**
   - Similarity index score: {{a_value_between_0.1_to_0.9}} (reflects how similar the images are overall).

2. **Itemized Damage Comparison:**
   - Pre-existing damages visible on the vehicle before loss: {{list_pre_existing_damages}}
   - Current damages visible on the vehicle after loss: {{list_current_damages}}
   - Distinctive differences: {{list_itemized_changes_between_images}} (itemize both additions and removals of damages or parts).

3. **Fraudulent Claim Detection:**
   - Claimant making a claim on pre-existing damage: {{Yes_or_No}}
   - Explanation: {{describe_why_the_claim_is_fraudulent_or_valid}}.

4. **Additional Notes:**
   - Image Quality: {{indicate_if_image_quality_is_too_low_for_analysis}}.
   - Human Review Recommendation: {{Yes_or_No}} (Recommend if the analysis is ambiguous or the case is complex).
   - Other Observations: {{any_additional_context_or_details_relevant_to_the_claim}}.

**Guidelines:**
- Provide as much specificity as possible when describing damages and differences.
- Focus on visible and verifiable details only; avoid speculative conclusions.
- Clearly separate observations related to the condition of the vehicle and any other unrelated aspects in the images.
- Highlight cases needing human intervention for further investigation.
"""

def SSIM(claim_details:str, image_urls: List[Dict[str, Any]]):
    # Dynamically load images from the provided URLs
    image_parts = []
    
    # Load pre-loss image
    pre_loss_image = next((img for img in image_urls if 'pre_loss' in img), None)
    if pre_loss_image:
        image_file = Part.from_uri(
            pre_loss_image['pre_loss'],
            mime_type="image/png",  # Consider making this dynamic
        )
        image_parts.append(image_file)
    
    # Load claim images
    claim_images = [img for img in image_urls if 'claim' in img]
    for claim_image in claim_images:
        image_file = Part.from_uri(
            claim_image['claim'],
            mime_type="image/png",  # Consider making this dynamic
        )
        image_parts.append(image_file)
    
    # Ensure we have at least one pre-loss image
    if not pre_loss_image:
        raise ValueError("A pre-loss image is required")
    # Ensure we have at least two images
    if len(image_parts) < 2:
        raise ValueError("At least two images are required")
    
    model = GenerativeModel("gemini-1.5-flash-002")
    
    # Combine images with prompts
    content = image_parts + [pre_prompt, prompt.format(claim_details=claim_details)]
    
    response = model.generate_content(content)
    return response.text
