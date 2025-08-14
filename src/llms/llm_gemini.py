import logging
import httpx

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gemini-1.5-pro"  # Valid current model; change if needed

    async def query(self, messages: list[dict]) -> str:
        # Convert messages to Gemini format: contents with user/model roles
        contents = []
        system_content = ""
        for msg in messages:
            if msg["role"] == "system":
                system_content += msg["content"] + "\n"  # Prepend system to first user
            elif msg["role"] == "user":
                content = system_content + msg["content"] if system_content else msg["content"]
                contents.append({"role": "user", "parts": [{"text": content}]})
                system_content = ""  # Clear after using
            elif msg["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})  # Gemini uses "model" for assistant

        if not contents:
            raise ValueError("No valid user messages provided")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
                headers={"x-goog-api-key": self.api_key},
                json={"contents": contents}
            )
            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.status_code} {response.text}")
            try:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError, TypeError) as e:
                raise Exception(f"Failed to parse Gemini response: {e}")