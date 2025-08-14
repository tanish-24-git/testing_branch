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
        # Added configurable LLM models
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.gpt_model = os.getenv("GPT_MODEL", "gpt-4o")
        self.grok_model = os.getenv("GROK_MODEL", "grok-beta")
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        if not self.openai_api_key and not self.gemini_api_key and not self.grok_api_key and not self.groq_api_key:
            logger.warning("No LLM API keys found in .env")

settings = Settings()