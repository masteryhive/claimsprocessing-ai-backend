import json
from src.config.appconfig import env_config
from vertexai.preview.generative_models import (
    GenerationResponse,
    GenerativeModel,
    GenerationConfig,
    HarmBlockThreshold,
    HarmCategory,
    Part,
)
from google.cloud import aiplatform
aiplatform.init(project=env_config.project_id)
from src.config.appconfig import env_config
from vertexai.generative_models import GenerativeModel, Part
from typing import Any, Dict, Iterable, List, Tuple

MODEL_NAME = "gemini-1.5-pro-002"

model = GenerativeModel(MODEL_NAME)
BLOCK_LEVEL = HarmBlockThreshold.BLOCK_ONLY_HIGH


def run_llm(response_schema:dict,prompt:str,
                max_output_tokens: int = 2048,
    temperature: int = 2,
    top_p: float = 0.7,
    stream: bool = False,):
        model = GenerativeModel("gemini-1.5-flash-002")
        response = model.generate_content([prompt],
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
        final_result = json.loads(response.candidates[0].content.parts[0].text)
        return final_result

