import httpx
import re
from typing import List, Dict
from .llm_base import LLMBase
from ..settings import settings

class GeminiClient(LLMBase):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = settings.gemini_model

    async def query(self, messages: List[Dict]) -> str:
        contents = []
        for msg in messages:
            contents.append({"role": "user" if msg["role"] == "user" else "model", "parts": [{"text": msg["content"]}]})
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                headers={"x-goog-api-key": self.api_key},
                json={"contents": contents}
            )
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]