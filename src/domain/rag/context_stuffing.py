
from datetime import datetime
import time
from typing import Iterable
from vertexai.preview.generative_models import (
    GenerationResponse,
    GenerativeModel,
       GenerationConfig,
    HarmBlockThreshold,
    HarmCategory,
    Part
)


MODEL_NAME = "gemini-1.5-pro-002" 

model = GenerativeModel(MODEL_NAME)
BLOCK_LEVEL = HarmBlockThreshold.BLOCK_ONLY_HIGH

def _get_datetime():
    """
    Get the current date and time in the format "Month Day Year".
    
    Returns:
        str: The current date and time in the format "Month Day Year".
    """
    now = datetime.now()
    return now.strftime("%B %d %Y")


def generate(
    prompt: list,
        response_schema:dict,
    max_output_tokens: int = 2048,
    temperature: int = 2,
    top_p: float = 0.4,
    stream: bool = False,
) -> GenerationResponse | Iterable[GenerationResponse]:
    """
    Function to generate response using Gemini 1.5 Pro

    Args:
        prompt:
            List of prompt parts
        max_output_tokens:
            Max Output tokens
        temperature:
            Temperature for the model
        top_p:
            Top-p for the model
        stream:
            Strem results?

    Returns:
        Model response

    """
    responses = model.generate_content(
        prompt,
          generation_config=GenerationConfig(
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            temperature=temperature,
        response_mime_type="application/json", response_schema=response_schema
    ),
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: BLOCK_LEVEL,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: BLOCK_LEVEL,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: BLOCK_LEVEL,
            HarmCategory.HARM_CATEGORY_HARASSMENT: BLOCK_LEVEL,
        },
        stream=stream,
    )

    return responses



    
def retry_generate(pdf_document: Part, prompt: str,response_schema:dict):
    predicted = False
    while not predicted:
        try:
            response = generate(
                prompt=[pdf_document, prompt.format(current_date=_get_datetime())],
                response_schema=response_schema
            )
        except Exception as e:
            print("sleeping for 2 seconds ...")
            print(e)
            time.sleep(2)
        else:
            predicted = True

    return response

def process_query(prompt: str,  pdf_path:str,response_schema:dict) -> str:
    with open(pdf_path, "rb") as fp:
        pdf_document = Part.from_data(data=fp.read(), mime_type="application/pdf")

    response = retry_generate(pdf_document,prompt,response_schema)
    return response.candidates[0].content.parts[0].text


# response_schema = {
#         "type": "object",
#         "properties": {
#    "PolicyBasics": {
#                 "type": "object",
#                 "properties": {
#                     "PolicyPeriod": {
#                      "type": "object",
#                         "properties": {
#                              "From": {
#                                 "type":  "string",
#                                 "description": "The start date of the policy period, typically found in sections labeled 'policy period' or 'coverage dates'.",
#                             },
#                               "To": {
#                                 "type":  "string",
#                                 "description": "The end date of the policy period, typically found in sections labeled 'policy period' or 'coverage dates'.",
#                             },
#                     },
#                     },
#                     "PolicyType": {
#                         "type": "string",
#                         "description": "Type of policy and coverage category (e.g., 'comprehensive', 'third-party').",
#                     },
#                     "PremiumDetails": {
#                         "type": "object",
#                         "properties": {
#                             "AnnualPremium": {
#                                 "type": "string",
#                                 "description": "The annual premium amount, from terms such as 'yearly cost' or 'premium amount'.",
#                             },
#                             "PaidAmount": {
#                            "type": "string",
#                                 "description": "The amount already paid, sometimes labeled as 'installments paid'.",
#                             },
#                             "PaymentTerms": {
#                                 "type": "string",
#                                 "description": "Payment terms such as 'monthly', 'quarterly', or 'annually'.",
#                             },
#                         },
#                     },
#                     "PolicyholderDetails": {
#                         "type": "string",
#                         "description": "Details about the policyholder, from fields like 'insured name', 'customer info', etc.",
#                     },
#                 },
#             },
                    
#                     }
#     }


# print(process_query("""Please, analyze this motor insurance policy document comprehensively and provide all information.
# The current date(YYYY-MM-DD) is {current_date}.""",  "src/teams/policy_doc/ZG-P-1000-010101-22-000346.pdf",response_schema))