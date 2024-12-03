"""Initiate the LLM on Vertex AI"""
from langchain_google_vertexai import ChatVertexAI


llm = ChatVertexAI(
    model="gemini-1.5-pro-001",
    temperature=0.2,
    max_tokens=8192,
    max_retries=6,
    stop=None,
)
