import base64
import httpx
from vertexai.preview.generative_models import (
    GenerationResponse,
    GenerativeModel,
    GenerationConfig,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)
from src.config.appconfig import env_config
from vertexai.generative_models import GenerativeModel, Part
from typing import Any, Dict, Iterable, List, Tuple

MODEL_NAME = "gemini-1.5-pro-002"

model = GenerativeModel(MODEL_NAME)
BLOCK_LEVEL = HarmBlockThreshold.BLOCK_ONLY_HIGH


pre_prompt = """
This is the image of the vehicle before loss, used as a reference for comparison.
"""


response_schema = {
    "type": "object",
    "properties": {
        "ImageSimilarityAnalysis": {
            "type": "object",
            "properties": {
                "SimilarityIndexScore": {
                    "type": "number",
                    "description": "A value between 0.1 to 0.9 reflecting how similar the images are overall. (Is it the same car?, Do they have the same color?, Is it the same body design?)",
                }
            },
        },
        "ItemizedDamageComparison": {
            "type": "object",
            "properties": {
                "PreExistingDamages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of pre-existing damages visible on the vehicle before loss.",
                },
                "CurrentDamages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of current damages visible on the vehicle after loss.",
                },
                "DistinctiveDifferences": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of itemized changes between images, including both additions and removals of damages or parts.",
                },
            },
        },
        "FraudulentClaimDetection": {
            "type": "object",
            "properties": {
                "ClaimOnPreExistingDamage": {
                    "type": "string",
                    "enum": ["Yes", "No"],
                    "description": "Indicates if the claimant is making a claim on pre-existing damage.",
                },
                "Explanation": {
                    "type": "string",
                    "description": "Description of why the claim is fraudulent or valid.",
                },
            },
        },
        "AdditionalNotes": {
            "type": "object",
            "properties": {
                "ImageQuality": {
                    "type": "string",
                    "description": "Indicates if the image quality is too low for analysis.",
                },
                "HumanReviewRecommendation": {
                    "type": "string",
                    "enum": ["Yes", "No"],
                    "description": "Recommendation for human review if the analysis is ambiguous or the case is complex.",
                },
                "OtherObservations": {
                    "type": "string",
                    "description": "Any additional context or details relevant to the claim.",
                },
            },
        },
    },
}


def get_mime_type(image_url: str) -> Part:
    if image_url.endswith(".png"):
        return Part.from_uri(
            image_url,
            mime_type="image/png",
        )
    elif image_url.endswith(".jpeg") or image_url.endswith(".jpg"):
        return Part.from_uri(
            image_url,
            mime_type="image/jpeg",
        )
    elif image_url.endswith(".webp"):
        return Part.from_uri(
            image_url,
            mime_type="image/webp",
        )
    elif image_url.endswith(".heic"):
        return Part.from_uri(
            image_url,
            mime_type="image/heic",
        )
    elif image_url.endswith(".heif"):
        return Part.from_uri(
            image_url,
            mime_type="image/heif",
        )
    else:
        raise ValueError("Unsupported image format for pre-loss image")

def structural_similarity_index_measure(
    claim_details: str,
    image_urls: List[Dict[str, Any]],
    max_output_tokens: int = 2048,
    temperature: int = 2,
    top_p: float = 0.7,
    stream: bool = False,
) -> GenerationResponse | Iterable[GenerationResponse]:
    prompt = """
Objective:
Perform a comprehensive analysis of vehicle images to evaluate pre-existing conditions and detect potential new damages for insurance claim assessment.

Claimant Claim details:
{claim_details}

Image Analysis Protocol:
Compare the "image of the vehicle before loss" with the other provided image(s) and perform the following evaluations:

**Guidelines:**
- Provide as much specificity as possible when describing damages and differences.
- Focus on visible and verifiable details only; avoid speculative conclusions.
- Clearly separate observations related to the condition of the vehicle and any other unrelated aspects in the images.
- Highlight cases needing human intervention for further investigation.
"""
    #TODO: make preloss and claim images a list images, incase of more than one image is provided
    # Dynamically load images from the provided URLs
    image_parts = []
    pre_loss_image = {}
    claim_image = {}
    try:
        # Load pre-loss image
        for item in image_urls:
            pre_loss_image = get_mime_type(item.get("prelossUrl", {}))
            claim_image = get_mime_type(item.get("claimUrl", {}))

        # Load claim images
        # if claim_image:
        #     image_parts.append(get_mime_type(claim_image))

        # for claim_image in claim_images:
        #     mime_type = get_mime_type(claim_image['claimUrl'])
        #     image_file = Part.from_uri(
        #         claim_image['claimUrl'],
        #         mime_type=mime_type,
        #     )
        #     image_parts.append(image_file)

        # Ensure we have at least one pre-loss image
        if not pre_loss_image:
            raise ValueError("A pre-loss image is required")
        # Ensure we have at least two images
        # if len(image_parts) < 2:
        #     raise ValueError("At least two images are required")

        model = GenerativeModel("gemini-1.5-flash-002")
        print( [
            pre_loss_image,
            claim_image,
        prompt.format(claim_details=claim_details),
        ])
        response = model.generate_content(
            [
            pre_loss_image,
            claim_image,
        prompt.format(claim_details=claim_details),
        ],
            generation_config=GenerationConfig(
                max_output_tokens=max_output_tokens,
                top_p=top_p,
                temperature=temperature,
                response_mime_type="application/json",
                response_schema=response_schema,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: BLOCK_LEVEL,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: BLOCK_LEVEL,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: BLOCK_LEVEL,
                HarmCategory.HARM_CATEGORY_HARASSMENT: BLOCK_LEVEL,
            },
            stream=stream,
        )
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        print(e)

# print(
#     structural_similarity_index_measure(
#         "",
#         [
#             {
#                 "prelossUrl": "gs://masteryhive-insurance-claims/rawtest/preloss/preloss_ZG-P-1000-010101-22-000346.jpg",
#                 "claimUrl": "gs://masteryhive-insurance-claims/rawtest/Scenario2/damaged_hyundai.jpg",
#             }
#         ],
#     )
# )
