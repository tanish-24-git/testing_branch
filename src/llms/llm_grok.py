import logging
import httpx
from .llm_base import LLMBase
from src.settings import settings

logger = logging.getLogger(__name__)

class GrokClient(LLMBase):
    supports_vision = False

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = settings.grok_model

    async def query(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": messages
                }
            )
            if response.status_code != 200:
                raise Exception(f"Grok API error: {response.status_code} {response.text}")
            try:
                return response.json()["choices"][0]["message"]["content"]
            except (KeyError, IndexError, TypeError) as e:
                raise Exception(f"Failed to parse Grok response: {e}")