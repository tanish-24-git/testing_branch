from abc import ABC, abstractmethod
from typing import List, Dict

class LLMBase(ABC):
    @abstractmethod
    async def query(self, messages: List[Dict]) -> str:
        pass