from typing import Dict
import logging
from .base_agent import BaseAgent
from .email_agent import EmailAgent
from .browser.browser_agent import BrowserAgent  # New import

logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self, llm_manager):
        self.agents: Dict[str, BaseAgent] = {}
        self.llm_manager = llm_manager

    def register_agents(self):
        self.agents["email"] = EmailAgent(self.llm_manager, {})
        self.agents["browser"] = BrowserAgent(self.llm_manager, {})  # Register BrowserAgent

    async def start_all(self):
        for agent in self.agents.values():
            await agent.start()

    async def stop_all(self):
        for agent in self.agents.values():
            await agent.stop()

    def get_agent(self, name: str) -> BaseAgent:
        return self.agents.get(name)

    async def route_command(self, command: str, context: Dict = None) -> str:
        # Simple routing: Check for browser keywords, else email or LLM
        if any(word in command.lower() for word in ["search", "open", "download", "summarize"]):
            agent = self.get_agent("browser")
            if agent:
                return await agent.process_command(command, context)
        agent = self.get_agent("email")
        if agent:
            return await agent.process_command(command, context)
        return await self.llm_manager.process(command, context)