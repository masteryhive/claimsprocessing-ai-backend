# import libraries
import httpx, base64
from langchain_google_vertexai import ChatVertexAI
from src.ai.llm import llm


def claims_image_evidence_recognizer(image_url: str) -> str:
    base64_image = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
    prompt = """Identify what is in this image. 
If it is related to a car, respond with which part(s) of the car appears damaged.
if it is not respond with 'not a valid image evidence for claims'.
Always provide your response as <answer> //your response </answer>"""
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
