import logging
import asyncio
import httpx
from src.llms.llm_grok import GrokClient
from src.llms.llm_gpt import GPTClient
from src.llms.llm_gemini import GeminiClient
from src.llms.llm_groq import GroqClient
from src.settings import settings

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self):
        self.clients = []
        if settings.groq_api_key:
            self.clients.append(GroqClient(settings.groq_api_key))
            logger.info("GroqClient initialized")
        else:
            logger.warning("No Groq API key found in .env")
        # Temporarily disable other LLMs to avoid quota errors
        # if settings.grok_api_key:
        #     self.clients.append(GrokClient(settings.grok_api_key))
        #     logger.info("GrokClient initialized")
        # if settings.openai_api_key:
        #     self.clients.append(GPTClient(settings.openai_api_key))
        #     logger.info("GPTClient initialized")
        # if settings.gemini_api_key:
        #     self.clients.append(GeminiClient(settings.gemini_api_key))
        #     logger.info("GeminiClient initialized")

    async def query_with_retry(self, client, messages: list[dict]) -> tuple[str, str]:
        """Query a client with retry logic for rate limits."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await client.query(messages)
                return result, None
            except Exception as e:
                error_str = str(e)
                if "429" in error_str:  # Rate limit error
                    retry_delay = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"Rate limit for {type(client).__name__}, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                    continue
                return None, f"Error with {type(client).__name__}: {error_str}"
        return None, f"Failed after {max_retries} retries for {type(client).__name__}"

    async def query_all(self, messages: list[dict], is_vision: bool) -> dict:
        responses = {}
        errors = []
        for client in self.clients:
            if is_vision and not client.supports_vision:
                errors.append(f"Skipped {type(client).__name__}: Does not support vision")
                continue
            result, error = await self.query_with_retry(client, messages)
            if result:
                responses[type(client).__name__] = result
            if error:
                errors.append(error)
        if not responses and errors:
            logger.error("\n".join(errors))
        return responses

    async def process(self, command: str, context: dict) -> str:
        image_data = context.get("image_data")
        mime_type = context.get("mime_type", "image/jpeg")
        is_vision = bool(image_data)
        context_str = "\n".join([f"{key}: {value}" for key, value in context.items() if key not in ["image_data", "mime_type"]])
        system_content = f"Current context:\n{context_str}" if context_str else ""
        if is_vision:
            user_content = [
                {"type": "text", "text": command},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}}
            ]
        else:
            user_content = command
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ]
        responses = await self.query_all(messages, is_vision)
        if responses:
            # Select the best (e.g., longest response)
            best_key = max(responses, key=lambda k: len(responses[k]))
            return responses[best_key]
        else:
            # Fallback with detailed error
            return "Sorry, I couldn't get a response from any available LLMs. Ensure API keys have sufficient credits/quota:\n" + \
                   "- Groq: Verify API key and model availability at https://console.groq.com\n" + \
                   "- Grok: Check credits at https://console.x.ai\n" + \
                   "- OpenAI: Check quota at https://platform.openai.com\n" + \
                   "- Gemini: Check quota at https://ai.google.dev"