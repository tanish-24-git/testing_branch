import logging
from src.llms.llm_grok import GrokClient
from src.llms.llm_gpt import GPTClient
from src.llms.llm_gemini import GeminiClient
from src.llms.llm_groq import GroqClient
from src.settings import settings

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self):
        self.clients = []
        if settings.grok_api_key:
            self.clients.append(GrokClient(settings.grok_api_key))
        if settings.openai_api_key:
            self.clients.append(GPTClient(settings.openai_api_key))
        if settings.gemini_api_key:
            self.clients.append(GeminiClient(settings.gemini_api_key))
        if settings.groq_api_key:
            self.clients.append(GroqClient(settings.groq_api_key))

    async def query_all(self, messages: list[dict]) -> dict:
        responses = {}
        for client in self.clients:
            try:
                result = await client.query(messages)
                responses[type(client).__name__] = result
            except Exception as e:
                logger.error(f"Error with {type(client).__name__}: {e}")
        return responses

    async def process(self, command: str, context: dict) -> str:
        context_str = "\n".join([f"{key}: {value}" for key, value in context.items()])
        messages = [
            {"role": "system", "content": f"Current context:\n{context_str}"},
            {"role": "user", "content": command}
        ]
        responses = await self.query_all(messages)
        # Compare and select best (simple: choose the longest response)
        if responses:
            best_key = max(responses, key=lambda k: len(responses[k]))
            return responses[best_key]
        raise Exception("All LLM clients failed")