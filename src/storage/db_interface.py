from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class DatabaseInterface(ABC):
    @abstractmethod
    async def save_automation_log(self, command: str, result: str):
        pass

    @abstractmethod
    async def get_automation_history(self, user_id: str) -> list:
        pass

class MockDatabase(DatabaseInterface):
    def __init__(self):
        self.logs = []

    async def save_automation_log(self, command: str, result: str):
        logger.info(f"Mock DB: Saving log - Command: {command}, Result: {result}")
        self.logs.append({"command": command, "result": result})

    async def get_automation_history(self, user_id: str) -> list:
        logger.info(f"Mock DB: Retrieving history for user {user_id}")
        return self.logs