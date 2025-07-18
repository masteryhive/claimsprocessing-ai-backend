from vertexai.preview.generative_models import (
    GenerationResponse,
    GenerativeModel,
    GenerationConfig,
    HarmBlockThreshold,
    HarmCategory,
    Part
)
from src.config.appconfig import env_config
from vertexai.generative_models import GenerativeModel, Part
from typing import Any, Dict, List
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import requests
from io import BytesIO
from PIL import Image

MODEL_NAME = "gemini-1.5-pro-002" 
model = GenerativeModel(MODEL_NAME)
BLOCK_LEVEL = HarmBlockThreshold.BLOCK_ONLY_HIGH

def load_and_preprocess_image(image_url: str) -> np.ndarray:
    """Load and preprocess image from URL for SSIM analysis."""
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    # Convert to grayscale and resize to standard size for comparison
    img = img.convert('L')
    img = img.resize((512, 512))  # Standard size for comparison
    return np.array(img)

def calculate_ssim_score(img1: np.ndarray, img2: np.ndarray) -> float:
    """Calculate SSIM score between two images."""
    score = ssim(img1, img2, full=False)
    # Normalize to 0.1-0.9 range as requested in the prompt
    normalized_score = 0.1 + (0.8 * max(0, min(1, score)))
    return round(normalized_score, 2)

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
   - Similarity index score: {ssim_score} (reflects how similar the images are overall, based on structural similarity analysis).

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
- The similarity score of {ssim_score} indicates the overall structural similarity between the images, where 0.1 means completely different and 0.9 means highly similar.
- Provide as much specificity as possible when describing damages and differences.
- Focus on visible and verifiable details only; avoid speculative conclusions.
- Clearly separate observations related to the condition of the vehicle and any other unrelated aspects in the images.
- Highlight cases needing human intervention for further investigation.
"""

def my_func(claim_details: str, image_urls: List[Dict[str, Any]],
    max_output_tokens: int = 2048,
    temperature: int = 2,
    top_p: float = 0.4,
    stream: bool = False,):
    
    # Load and process images for SSIM
    pre_loss_image = next((img for img in image_urls if 'pre_loss' in img), None)
    if not pre_loss_image:
        raise ValueError("A pre-loss image is required")
    
    # Process pre-loss image for SSIM
    pre_loss_array = load_and_preprocess_image(pre_loss_image['pre_loss'])
    
    # Load claim images
    claim_images = [img for img in image_urls if 'claim' in img]
    if not claim_images:
        raise ValueError("At least one claim image is required")
    
    # Calculate SSIM scores for each claim image
    ssim_scores = []
    for claim_image in claim_images:
        claim_array = load_and_preprocess_image(claim_image['claim'])
        ssim_score = calculate_ssim_score(pre_loss_array, claim_array)
        ssim_scores.append(ssim_score)
    
    # Use average SSIM score if multiple claim images
    average_ssim = sum(ssim_scores) / len(ssim_scores)
    
    # Prepare image parts for Gemini
    image_parts = []
    image_parts.append(Part.from_uri(
        pre_loss_image['pre_loss'],
        mime_type="image/png",
    ))
    
    for claim_image in claim_images:
        image_parts.append(Part.from_uri(
            claim_image['claim'],
            mime_type="image/png",
        ))
    
    # Format prompt with SSIM score
    formatted_prompt = prompt.format(
        claim_details=claim_details,
        ssim_score=average_ssim
    )
    
    # Combine images with prompts
    full_prompt = image_parts + [pre_prompt, formatted_prompt]
    
    model = GenerativeModel("gemini-1.5-flash-002")
    
    response = model.generate_content(
        full_prompt,
        generation_config=GenerationConfig(
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=response_schema
        ),
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: BLOCK_LEVEL,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: BLOCK_LEVEL,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: BLOCK_LEVEL,
            HarmCategory.HARM_CATEGORY_HARASSMENT: BLOCK_LEVEL,
        },
        stream=stream,
    )
    return response.text