import logging

logger = logging.getLogger(__name__)

class ComparisonPipeline:
    def __init__(self, llm_manager, rag):
        self.llm_manager = llm_manager
        self.rag = rag

    async def process(self, command: str, context: dict = {}):
        rag_response = self.rag.retrieve(command)
        context["rag"] = rag_response
        result = await self.llm_manager.process(command, context)
        return result