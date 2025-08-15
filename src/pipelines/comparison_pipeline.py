import logging
from src.llm_manager import LLMManager
from src.rag import RAG

logger = logging.getLogger(__name__)

class ComparisonPipeline:
    def __init__(self, llm_manager: LLMManager,):
        self.llm_manager = llm_manager
        
    async def process(self, command: str, context: dict = {}):
        result = await self.llm_manager.process(command, context)
        logger.info(f"Processed command: {command}, result: {result}")
        return result