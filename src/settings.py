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
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")  # Changed: Use gemini-1.5-flash
        self.gpt_model = os.getenv("GPT_MODEL", "gpt-4o")
        self.grok_model = os.getenv("GROK_MODEL", "grok-beta")
        self.groq_model = os.getenv("GROQ_MODEL", "llama3-70b-8192")  # Changed: Use supported Groq model
        if not any([self.openai_api_key, self.gemini_api_key, self.grok_api_key, self.groq_api_key]):
            logger.warning("No LLM API keys found in .env")

settings = Settings()