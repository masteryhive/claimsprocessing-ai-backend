# import libraries
from typing import Any, Dict, List
import httpx, base64
from src.ai.llm import llm
import vertexai
from src.config.appconfig import env_config
from vertexai.generative_models import GenerativeModel, Part


vertexai.init(project=env_config.project_id, location=env_config.region)

async def fetch_image(image_url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url, timeout=300)
    return base64.b64encode(response.content).decode("utf-8")

async def claims_image_evidence_recognizer(image_url: str) -> str:
    base64_image = await fetch_image(image_url)
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
This is the image of the vehicle before loss.
"""
prompt = """
Objective:
Perform a comprehensive analysis of vehicle images to determine pre-existing conditions and potential damage for insurance claim evaluation.

Image Analysis Protocol:
Perform an image similarity comparison between the "image of the vehicle before loss" and the other image(s).

[TEMPLATE]
 - similarity index score: {{a_value_between_0.1_to_0.9}}
 - distinctive differences: {{itemize_visible_damages_on_the_vehicle_before_loss_and_current_damages_on_the_vehicle}}
 - Fraudulent Claim: {{is_the_claimant_making_a_claim_for_a_damage_that_already_existed_on_the_vehicle}} <-- should be either Yes orr No -->

**Additional Notes:**

* **Clarity and Detail:** Be as specific as possible when describing the damage.
* **Image Quality:** If the image quality is too poor to assess the damage or extract information, indicate this in the output.
* **Human Intervention:** For complex or ambiguous cases, suggest that it should be highlighted to the human claim officer.
"""

def SSIM(image_urls: List[Dict[str, Any]]):
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
    content = image_parts + [pre_prompt, prompt]
    
    response = model.generate_content(content)
    print(response.text)
    return response