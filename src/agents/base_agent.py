"""
Base Agent Class - Foundation for all AI agents
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents
    Provides common functionality and interface
    """
    
    def __init__(self, name: str, llm_manager=None, config: Dict = None):
        self.name = name
        self.llm_manager = llm_manager
        self.config = config or {}
        self.is_active = False
        self.last_activity = None
        self.conversation_history = []
        self.context_memory = {}
        
        logger.info(f"Initialized {self.name} agent")
    
    @abstractmethod
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Process a command and return response"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the agent"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup resources"""
        pass
    
    async def start(self) -> bool:
        """Start the agent"""
        try:
            if await self.initialize():
                self.is_active = True
                self.last_activity = datetime.now()
                logger.info(f"{self.name} agent started successfully")
                return True
            else:
                logger.error(f"Failed to initialize {self.name} agent")
                return False
        except Exception as e:
            logger.error(f"Error starting {self.name} agent: {e}")
            return False
    
    async def stop(self):
        """Stop the agent"""
        try:
            await self.cleanup()
            self.is_active = False
            logger.info(f"{self.name} agent stopped")
        except Exception as e:
            logger.error(f"Error stopping {self.name} agent: {e}")
    
    def add_to_history(self, command: str, response: str, metadata: Dict = None):
        """Add interaction to conversation history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "response": response,
            "metadata": metadata or {}
        }
        self.conversation_history.append(entry)
        
        # Keep only last 50 interactions
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]
    
    def update_context(self, key: str, value: Any):
        """Update context memory"""
        self.context_memory[key] = value
        self.last_activity = datetime.now()
    
    def get_context(self, key: str, default=None):
        """Get value from context memory"""
        return self.context_memory.get(key, default)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "active": self.is_active,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "history_size": len(self.conversation_history),
            "context_keys": list(self.context_memory.keys())
        }
    
    async def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate response using LLM"""
        if not self.llm_manager:
            return "LLM not available"
        
        try:
            # Add agent context to the prompt
            agent_context = {
                "agent_name": self.name,
                "agent_type": self.__class__.__name__,
                "conversation_history": self.conversation_history[-5:],  # Last 5 interactions
                "context_memory": self.context_memory
            }
            
            # Merge contexts
            full_context = {**(context or {}), **agent_context}
            
            response = await self.llm_manager.process(prompt, full_context)
            return response
            
        except Exception as e:
            logger.error(f"Error generating response in {self.name} agent: {e}")
            return f"Error generating response: {e}"
    
    async def think(self, situation: str) -> str:
        """Let the agent 'think' about a situation"""
        thinking_prompt = f"""
        As an AI agent named {self.name}, analyze this situation and provide your thoughts:
        
        Situation: {situation}
        
        Consider:
        1. What actions might be needed?
        2. What information is missing?
        3. What are the potential risks/benefits?
        4. What would be the best approach?
        
        Provide a thoughtful analysis.
        """
        
        return await self.generate_response(thinking_prompt)
    
    def validate_command(self, command: str) -> tuple[bool, str]:
        """Validate if command is safe and appropriate for this agent"""
        # Basic validation - override in subclasses for specific validation
        if not command or not command.strip():
            return False, "Empty command"
        
        # Check for potentially dangerous commands
        dangerous_patterns = ['rm -rf', 'del /f', 'format c:', 'sudo rm', 'DROP TABLE']
        if any(pattern in command.lower() for pattern in dangerous_patterns):
            return False, "Potentially dangerous command detected"
        
        return True, "Command appears safe"
    
    async def handle_error(self, error: Exception, context: str = "") -> str:
        """Handle errors gracefully"""
        error_message = f"Error in {self.name} agent"
        if context:
            error_message += f" ({context})"
        error_message += f": {str(error)}"
        
        logger.error(error_message)
        
        # Try to generate a helpful error response
        try:
            error_prompt = f"""
            An error occurred in the {self.name} agent: {str(error)}
            Context: {context}
            
            Provide a helpful explanation of what went wrong and suggest possible solutions.
            Be concise and user-friendly.
            """
            
            helpful_response = await self.generate_response(error_prompt)
            return f"❌ {helpful_response}"
            
        except:
            # Fallback to basic error message
            return f"❌ An error occurred in {self.name} agent: {str(error)}"
    
    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name}, active={self.is_active})"
    
    def __repr__(self):
        return self.__str__()


class AgentManager:
    """Manages multiple AI agents"""
    
    def __init__(self, llm_manager=None):
        self.agents: Dict[str, BaseAgent] = {}
        self.llm_manager = llm_manager
        
    def register_agent(self, agent: BaseAgent):
        """Register a new agent"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def unregister_agent(self, agent_name: str):
        """Unregister an agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"Unregistered agent: {agent_name}")
    
    async def start_all_agents(self):
        """Start all registered agents"""
        results = {}
        for name, agent in self.agents.items():
            try:
                results[name] = await agent.start()
            except Exception as e:
                logger.error(f"Failed to start agent {name}: {e}")
                results[name] = False
        return results
    
    async def stop_all_agents(self):
        """Stop all agents"""
        for agent in self.agents.values():
            try:
                await agent.stop()
            except Exception as e:
                logger.error(f"Error stopping agent {agent.name}: {e}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def get_active_agents(self) -> List[BaseAgent]:
        """Get list of active agents"""
        return [agent for agent in self.agents.values() if agent.is_active]
    
    def get_all_status(self) -> Dict[str, Dict]:
        """Get status of all agents"""
        return {name: agent.get_status() for name, agent in self.agents.items()}
    
    async def route_command(self, command: str, preferred_agent: str = None) -> str:
        """Route command to appropriate agent"""
        # If preferred agent specified, use it
        if preferred_agent and preferred_agent in self.agents:
            agent = self.agents[preferred_agent]
            if agent.is_active:
                return await agent.process_command(command)
        
        # Otherwise, try to determine best agent for command
        best_agent = self._determine_best_agent(command)
        if best_agent:
            return await best_agent.process_command(command)
        
        return "No suitable agent found for this command"
    
    def _determine_best_agent(self, command: str) -> Optional[BaseAgent]:
        """Determine best agent for a command"""
        command_lower = command.lower()
        
        # Simple keyword-based routing
        if any(keyword in command_lower for keyword in ['email', 'mail', 'message']):
            return self.get_agent('email_agent')
        
        if any(keyword in command_lower for keyword in ['browser', 'web', 'open', 'navigate']):
            return self.get_agent('automation_agent')
        
        if any(keyword in command_lower for keyword in ['desktop', 'window', 'click', 'type']):
            return self.get_agent('automation_agent')
        
        # Default to first active agent
        active_agents = self.get_active_agents()
        return active_agents[0] if active_agents else None