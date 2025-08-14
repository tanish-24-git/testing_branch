import logging
import httpx
import re

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gemini-1.5-flash"  # Valid current model; change if needed
        self.supports_vision = True

    async def query(self, messages: list[dict]) -> str:
        # Convert messages to Gemini format: contents with user/model roles
        contents = []
        system_content = ""
        for msg in messages:
            if msg["role"] == "system":
                system_content += msg["content"] + "\n"  # Prepend system to first user
            elif msg["role"] == "user":
                parts = []
                if system_content:
                    parts.append({"text": system_content})
                    system_content = ""  # Clear after using
                content = msg["content"]
                if isinstance(content, str):
                    parts.append({"text": content})
                elif isinstance(content, list):
                    for item in content:
                        if item["type"] == "text":
                            parts.append({"text": item["text"]})
                        elif item["type"] == "image_url":
                            url = item["image_url"]["url"]
                            match = re.match(r"^data:(?P<mime>[^;]+);base64,(?P<data>.*)$", url)
                            if not match:
                                raise ValueError("Invalid image data URL")
                            parts.append({
                                "inline_data": {
                                    "mime_type": match.group("mime"),
                                    "data": match.group("data")
                                }
                            })
                else:
                    raise ValueError("Unsupported content type for user message")
                contents.append({"role": "user", "parts": parts})
            elif msg["role"] == "assistant":
                contents.append({"role": "model", "parts": [{"text": msg["content"]}]})  # Gemini uses "model" for assistant

        if not contents:
            raise ValueError("No valid user messages provided")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}",
                json={"contents": contents}
            )
            if response.status_code != 200:
                raise Exception(f"Gemini API error: {response.status_code} {response.text}")
            try:
                return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError, TypeError) as e:
                raise Exception(f"Failed to parse Gemini response: {e}")