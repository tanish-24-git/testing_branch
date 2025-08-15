# Enhanced AI Agent System
__version__ = "2.0.0"
__author__ = "AI Agent Development Team"
__description__ = "Enhanced AI Agent with Email Intelligence & Desktop Automation"

# Core modules
from .llm_manager import LLMManager
from .rag import RAG
from .config import config
from .settings import settings

__all__ = ['LLMManager', 'RAG', 'config', 'settings']