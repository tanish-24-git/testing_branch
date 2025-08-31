import logging
import asyncio
from typing import List, Dict, Tuple
from .llms.llm_base import LLMBase
from .llms.llm_gemini import GeminiClient
from .llms.llm_groq import GroqClient
from .settings import settings

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self):
        self.clients: List[LLMBase] = []
        if settings.gemini_api_key:
            self.clients.append(GeminiClient(settings.gemini_api_key))
        if settings.groq_api_key:
            self.clients.append(GroqClient(settings.groq_api_key))
        if not self.clients:
            logger.warning("No LLM clients initialized")

    async def query_with_retry(self, client: LLMBase, messages: List[Dict]) -> Tuple[str, str]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await client.query(messages)
                return result, None
            except Exception as e:
                error_str = str(e)
                if "429" in error_str:
                    retry_delay = (2 ** attempt) * 2
                    logger.warning(f"Rate limit for {type(client).__name__}, retrying in {retry_delay}s")
                    await asyncio.sleep(retry_delay)
                    continue
                return None, f"Error with {type(client).__name__}: {error_str}"
        return None, f"Failed after {max_retries} retries"

    async def process(self, command: str, context: Dict = {}) -> str:
        messages = [
            {"role": "system", "content": str(context)},
            {"role": "user", "content": command}
        ]
        responses = {}
        for client in self.clients:
            result, error = await self.query_with_retry(client, messages)
            if result:
                responses[type(client).__name__] = result
        if responses:
            return max(responses.values(), key=len)
        return "No valid responses from LLMs"