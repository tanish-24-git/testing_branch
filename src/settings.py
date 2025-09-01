
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class Settings:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")  # Optional
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.groq_model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
        if not any([self.gemini_api_key, self.groq_api_key]):
            logger.warning("No LLM API keys found")

settings = Settings()