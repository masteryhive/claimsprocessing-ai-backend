# import libraries
import httpx, base64
from src.ai.llm import llm

async def fetch_image(image_url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url, timeout=300)
    return base64.b64encode(response.content).decode("utf-8")

async def claims_image_evidence_recognizer(image_url: str) -> str:
    base64_image = await fetch_image(image_url)
    prompt = ("Identify what is in this image meant to serve as evidence for an vehicle insurance claim. "
"If it is related to a car, respond with which part(s) of the car appears damaged."
"if it is not respond with 'not a valid image evidence for claims'."
"Always provide your response as highly verbose as possible")
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
