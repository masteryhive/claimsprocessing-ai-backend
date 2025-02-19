# import libraries
from vertexai.preview.generative_models import (
    GenerationResponse,
    GenerativeModel,
    GenerationConfig,
)

import base64


MODEL_NAME = "gemini-1.5-pro-002"  

model = GenerativeModel(MODEL_NAME)


PROMPT_TEMPLATE = """
You are an expert in verifying the authenticity of {Country} Drivers Licenses based on strict verification criteria. Your task is to analyze the provided image and confirm whether it meets all the required security and formatting standards. 

#Task
The verification process must be precise and thorough. You **must** check and confirm that each of the following criteria is strictly met:

1. **General Structure & Layout**:
   - The card must be horizontally rectangular.
   - It must have the {Country_name} title at the top.
   - The "NATIONAL DRIVERS LICENCE" label must be positioned below the national title.
   - There should be a Nigerian flag on the top left.

2. **License Information Placement**:
   - The **LNO (License Number)** must be positioned at the top-left under the national title.
   - The **LICENSE CLASS** should be at the top-right.
   - The **Expiry Date (EXP)** should be positioned directly below the issue date.
   - The **Full Name** must be prominently displayed in uppercase.

3. **Personal & Biometric Data**:
   - A clear **passport-sized photograph** must be positioned on the right side.
   - The **signature of the license holder** must be visible at the bottom-left.
   - The **official signature of the issuing authority** must be at the bottom-right.
   - The **Height, Blood Group, and Sex** must be listed.
   - The **Date of Birth (DOB)** must be formatted correctly.

4. **Security Features & Authenticity**:
   - A visible **hologram security feature** must be present.
   - The **background must contain microprint security patterns**.
   - There should be a **unique identification number** that follows the Nigerian licensing format.
   - The **document must not contain irregular fonts, misalignment, or incorrect spacing**.
   - The license must not contain spelling errors.

5. **Color Scheme Verification**:
   - The background should have a **light beige or off-white color with subtle security patterns**.
   - The text should be **black and dark green**, ensuring readability.
   - The Nigerian flag should have its standard **green-white-green** coloration.
   - Security holograms may have a **gold or silver reflective tint**.

### Output:
- If the image **strictly meets all requirements**, return: **Valid**.
- If **any single criterion is missing or incorrect**, return: **Invalid**.

The verification **must be strictly enforced**. **No license should pass** unless every criterion is **fully** met.

**Image data (base64-encoded)** : {IMAGE_BASE64}
"""


RESPONSE_SCHEMA_STRUCT = {
    "type": "object",
    "properties": {
        "isValid": {
            "type": "string",
            "enum": ["valid", "invalid"],
            "description": "Indicates whether the card is valid. Allowed values: 'valid' or 'invalid'.",
        }
    },
    "required": ["isValid"],
}

def generate(
    image_path,
    temperature: float = 2.0,
    top_p: float = 0.8,
) -> GenerationResponse:
    
    """
    Generates a response using Gemini 1.5 Pro (text-based).
    
    Args:
        image_path: Path to the license image.
        temperature: Controls the randomness of the model's output.
        top_p: Top-p sampling for the model.
    
    Returns:
        A GenerationResponse from the Vertex AI generative model.
    """

    try:
        # Load the image
        with open(image_path, "rb") as f:
            image_data = f.read()

        image_b64 = base64.b64encode(image_data).decode("utf-8")

        prompt = PROMPT_TEMPLATE.format(IMAGE_BASE64=image_b64)

        # Attempt to generate
        responses = model.generate_content(
            [prompt],
            generation_config=GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA_STRUCT,
            ),
        )

        return responses
    except FileNotFoundError as e:
        raise ValueError(f"Image file not found at specified path: {image_path}") from e
    except Exception as e:
        raise RuntimeError(f"Error processing image or generating response: {str(e)}") from e