import logging
import httpx

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "llama-3.1-70b-versatile"  # Example model

    async def query(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "messages": messages
                }
            )
            if response.status_code != 200:
                raise Exception(f"Groq API error: {response.status_code} {response.text}")
            try:
                return response.json()["choices"][0]["message"]["content"]
            except (KeyError, IndexError, TypeError) as e:
                raise Exception(f"Failed to parse Groq response: {e}")