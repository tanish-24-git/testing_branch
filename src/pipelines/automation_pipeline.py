import logging
from src.llm_manager import LLMManager
from src.rag import RAG
from src.automation.chrome_automation import ChromeAutomation

logger = logging.getLogger(__name__)

class AutomationPipeline:
    def __init__(self, llm_manager: LLMManager, rag: RAG):
        self.llm_manager = llm_manager
        self.rag = rag
        self.automation = ChromeAutomation()

    async def process(self, command: str, context: dict = {}):
        # Check for sensitive actions
        if "submit form" in command.lower() or "make payment" in command.lower() or "send email" in command.lower():
            context["requires_confirmation"] = True
        result = await self.automation.execute_command(command, self.llm_manager, self.rag)
        logger.info(f"Automation command: {command}, result: {result}")
        return result