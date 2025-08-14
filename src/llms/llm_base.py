from abc import ABC, abstractmethod
from typing import List, Dict

class LLMBase(ABC):
    """
    Abstract base class for all LLM clients to enforce a consistent interface.
    """
    supports_vision: bool

    @abstractmethod
    async def query(self, messages: List[Dict[str, any]]) -> str:
        """
        Query the LLM with a list of messages.
        """
        pass