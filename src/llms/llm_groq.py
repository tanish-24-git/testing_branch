import httpx
from typing import List, Dict
from .llm_base import LLMBase
from ..settings import settings

class GroqClient(LLMBase):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = settings.groq_model

    async def query(self, messages: List[Dict]) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages}
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]