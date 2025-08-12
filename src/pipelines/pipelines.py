import logging
import importlib
import os
from src.llm_manager import LLMManager
from src.context_manager import ContextManager
from src.text_search import TextSearch
from src.agents import AgenticAI
from src.utils import extract_intent_entities
from src.config import config
from src.pipelines.handlers import BaseHandler

logger = logging.getLogger(__name__)

class CommandPipeline:
    def __init__(self):
        self.llm_manager = LLMManager()
        self.context_manager = ContextManager()
        self.text_search = TextSearch()
        self.agentic_ai = AgenticAI()
        self.head_handler = self._build_chain()

    def _build_chain(self):
        """Build chain-of-responsibility dynamically from config, plugins, code."""
        head = BaseHandler()
        current = head

        # From config
        for handler in config.get_handlers():
            current = current.set_next(handler)

        # From plugins dir
        plugins_dir = "src/plugins"
        for file in os.listdir(plugins_dir):
            if file.endswith(".py") and file != "__init__.py":
                module_name = f"src.plugins.{file[:-3]}"
                module = importlib.import_module(module_name)
                for attr in dir(module):
                    cls = getattr(module, attr)
                    if isinstance(cls, type) and issubclass(cls, BaseHandler) and cls != BaseHandler:
                        current = current.set_next(cls())

        # From code (hardcoded if needed)
        # Add more

        return head

    async def process(self, command: str, context=None):
        """Process command through pipeline."""
        if context is None:
            context = self.context_manager.enrich_context(command)

        intent, entities = extract_intent_entities(command)

        # Route through chain
        result = self.head_handler.handle(command, intent, entities, context)

        if result == "No handler found":
            return await self.llm_manager.fallback(command, intent, entities, context)

        # If complex, use agent
        if "complex" in intent:
            result = self.agentic_ai.execute_workflow(command)

        # Natural feedback
        return {"command": command, "result": f"Successfully {result}"}