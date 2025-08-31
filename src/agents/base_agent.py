from abc import ABC, abstractmethod
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, llm_manager, config: Dict):
        self.name = name
        self.llm_manager = llm_manager
        self.config = config

    @abstractmethod
    async def process_command(self, command: str, context: Dict = None) -> str:
        pass

    async def start(self):
        logger.info(f"Started {self.name} agent")

    async def stop(self):
        logger.info(f"Stopped {self.name} agent")