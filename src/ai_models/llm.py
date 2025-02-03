"""Initiate the LLM on Vertex AI"""
from langchain_google_vertexai import ChatVertexAI
from src.config.appconfig import env_config

# Gemini LLM instance on VertexAI
llm = ChatVertexAI(
    project_id = env_config.project_id,
    model="gemini-1.5-pro-002",
    temperature=0.2,
    max_tokens=8192,
    max_retries=6,
    stop=None,
)

llm_flash = ChatVertexAI(
    model="gemini-1.5-flash-002",
)