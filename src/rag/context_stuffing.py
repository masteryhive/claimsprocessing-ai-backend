
from datetime import datetime
import os
from typing import Iterable

import requests
from src.config.appconfig import env_config
import time

import vertexai
from vertexai.preview.generative_models import (
    GenerationResponse,
    GenerativeModel,
    HarmBlockThreshold,
    HarmCategory,
    Part
)

MODEL_NAME = "gemini-1.5-pro-002"  # Replace with model name

vertexai.init(project=env_config.project_id, location=env_config.region)
model = GenerativeModel(MODEL_NAME)
BLOCK_LEVEL = HarmBlockThreshold.BLOCK_ONLY_HIGH

def _get_datetime():
    now = datetime.now()
    return now.strftime("%B %d %Y")

context_prompt = """
Use the document above to answer the question below. Follow the Instructions and Suggestions below as a guide to answering the question.
The current date(YYYY-MM-DD) is {current_date}.

Confidence Scoring and Source Validation:
  Each response must include the following validation information:
  <validation>
  - Confidence Score: {{confidence_score}} (0.0-1.0)
  - Result Derivation: {{how you arrived at this result}}
  - Context section cited: {{Section from context where answer was found, including page number}}
  - Verification Status: {{verification_status}}
  </validation>
Confidence Scoring:
  - VERIFIED (1.0): Direct from authenticated source.
  - HIGHLY CONFIDENT (0.8-0.9): Multiple supporting sources.
  - MODERATELY CONFIDENT (0.6-0.7): Limited but reliable sources.
  - LOW CONFIDENCE (0.4-0.5): Inferred or uncertain.
  - SPECULATIVE (<0.4): Requires verification.
<Instructions>
- First, analyze the question below and return which variables need to be analyzed, from what insured period (example: 06/11/2020 - 15/10), and any other details present in the question.
- Then return an analysis of what is asked in the question.
- Finally, carefully analyze the document above and answer the question below completely and correctly, using the variables determined in the previous step.
- Explain how you arrived at this result.
- Answer ONLY what was asked.
CORE RESPONSE STRUCTURE:
  <answer>
  [your concise and relevant response here]
  </answer>
  <validation>
  - Confidence score: {{confidence_score}} (0.0-1.0)
  - Result Derivation: [Explain how you arrived at this result]
  - Context section cited: [Section from context where answer was found,including the page number]
  </validation>
<Instructions>
<Suggestions>
- The document above is a vehicle insurance policy document with various tables, graphs, infographics, lists, and additional information in text.
- PAY VERY CLOSE ATTENTION to the MEMORANDA, SCHEDULE and VEHICLE POLICY section to answer the question below.
- Use ONLY this document as context to answer the question below.
</Suggestions>
<Question>
From the policy_document, {question}
</Question>
answer:"""

def generate(
    prompt: list,
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
        generation_config={
            "max_output_tokens": max_output_tokens,
            "temperature": temperature,
            "top_p": top_p,
        },
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: BLOCK_LEVEL,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: BLOCK_LEVEL,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: BLOCK_LEVEL,
            HarmCategory.HARM_CATEGORY_HARASSMENT: BLOCK_LEVEL,
        },
        stream=stream,
    )

    return responses

def download_pdf(reference:str):
    base_url = "https://storage.googleapis.com/masteryhive-insurance-claims/rawtest/policy_document"
    modified_reference = reference.replace("/", "-")
    file_url = f"{base_url}/{modified_reference}.pdf"

    download_path = "src/ai/rag/doc"

    # Ensure the download directory exists
    os.makedirs(download_path, exist_ok=True)

    # Download the file
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(download_path, f"{modified_reference}.pdf")
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        return "File downloaded successfully"
    else:
        return f"Failed to download the file. HTTP status code: {response.status_code}"
        
def retry_generate(pdf_document: Part, prompt: str, question: str):
    predicted = False
    while not predicted:
        try:
            response = generate(
                prompt=[pdf_document, prompt.format(question=question,current_date=_get_datetime())]
            )
        except Exception as e:
            print("sleeping for 2 seconds ...")
            print(e)
            time.sleep(2)
        else:
            predicted = True

    return response

def process_query(query: str,  pdf_path:str, prompt: str = context_prompt) -> None:
    with open(pdf_path, "rb") as fp:
        pdf_document = Part.from_data(data=fp.read(), mime_type="application/pdf")

    response = retry_generate(pdf_document, prompt, query)
    return response.text
