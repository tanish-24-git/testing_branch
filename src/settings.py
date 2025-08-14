from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class Settings:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.grok_api_key = os.getenv("GROK_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.openai_api_key and not self.gemini_api_key and not self.grok_api_key and not self.groq_api_key:
            logger.warning("No LLM API keys found in .env")

settings = Settings()