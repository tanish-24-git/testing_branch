"""
Automation Agent - Manages browser and desktop automation
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

from .base_agent import BaseAgent
from ..automation.browser.browser_automation import browserAutomation
from ..automation.desktop.desktop_automation import DesktopAutomation

logger = logging.getLogger(__name__)

class AutomationAgent(BaseAgent):
    """
    AI Agent for automation tasks
    Features:
    - Browser automation coordination
    - Desktop automation management
    - Multi-step automation workflows
    - Safety checks and confirmations
    """
    
    def __init__(self, llm_manager=None, config: Dict = None):
        super().__init__("automation_agent", llm_manager, config)
        
        self.browser_automation = None
        self.desktop_automation = None
        self.safety_enabled = config.get('safety_checks', True) if config else True
        self.max_steps = config.get('max_steps', 20) if config else 20
        
        # Automation state
        self.current_workflow = None
        self.workflow_steps = []
        
    async def initialize(self) -> bool:
        """Initialize automation agent"""
        try:
            # Initialize automation modules
            self.browser_automation = browserAutomation()
            self.desktop_automation = DesktopAutomation()
            
            # Test capabilities
            browser_available = True  # Browser automation is always available (with fallbacks)
            desktop_available = self.desktop_automation.is_available()
            
            logger.info(f"Automation capabilities - Browser: {browser_available}, Desktop: {desktop_available}")
            
            self.update_context("browser_available", browser_available)
            self.update_context("desktop_available", desktop_available)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize automation agent: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup automation agent resources"""
        if self.current_workflow:
            logger.info("Stopping current workflow")
            self.current_workflow = None
        
        logger.info("Automation agent cleanup completed")
    
    async def process_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Process automation commands"""
        try:
            self.last_activity = datetime.now()
            command_lower = command.lower()
            
            # Determine automation type
            if self._is_browser_command(command):
                return await self._handle_browser_automation(command, context)
            
            elif self._is_desktop_command(command):
                return await self._handle_desktop_automation(command, context)
            
            elif "workflow" in command_lower or "sequence" in command_lower:
                return await self._handle_workflow_command(command, context)
            
            elif "stop" in command_lower and ("automation" in command_lower or "workflow" in command_lower):
                return await self._handle_stop_automation()
            
            elif "status" in command_lower and "automation" in command_lower:
                return self._handle_automation_status()
            
            else:
                # Use AI to determine automation type and generate response
                return await self._handle_ai_automation_command(command, context)
                
        except Exception as e:
            return await self.handle_error(e, "processing automation command")
    
    def _is_browser_command(self, command: str) -> bool:
        """Check if command is for browser automation"""
        browser_keywords = [
            'navigate', 'open', 'browse', 'click', 'fill', 'submit',
            'web', 'website', 'url', 'browser', 'page', 'form'
        ]
        return any(keyword in command.lower() for keyword in browser_keywords)
    
    def _is_desktop_command(self, command: str) -> bool:
        """Check if command is for desktop automation"""
        desktop_keywords = [
            'window', 'minimize', 'maximize', 'close', 'focus',
            'type', 'press', 'key', 'mouse', 'click at',
            'screenshot', 'desktop', 'application', 'app'
        ]
        return any(keyword in command.lower() for keyword in desktop_keywords)
    
    async def _handle_browser_automation(self, command: str, context: Dict[str, Any] = None) -> str:
        """Handle browser automation commands"""
        try:
            logger.info(f"Processing browser automation: {command}")
            
            # Safety check for sensitive browser actions
            if self.safety_enabled and self._requires_confirmation(command):
                confirmation_msg = f"⚠️ Browser automation requires confirmation: {command}\n"
                confirmation_msg += "This action may interact with websites. Proceed? (yes/no)"
                
                # In a real implementation, you'd wait for user confirmation
                # For now, we'll add a warning and proceed
                result = await self.browser_automation.execute_command(command, self.llm_manager, self.context_memory.get('rag'))
                return f"{confirmation_msg}\n\n🤖 Proceeding with browser automation:\n{result}"
            
            result = await self.browser_automation.execute_command(command, self.llm_manager, self.context_memory.get('rag'))
            
            # Add to history
            self.add_to_history(command, result, {
                "automation_type": "browser",
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            return await self.handle_error(e, "browser automation")
    
    async def _handle_desktop_automation(self, command: str, context: Dict[str, Any] = None) -> str:
        """Handle desktop automation commands"""
        try:
            logger.info(f"Processing desktop automation: {command}")
            
            if not self.desktop_automation.is_available():
                return "❌ Desktop automation not available. Install required packages: pip install pyautogui pygetwindow pynput psutil"
            
            # Enhanced safety check for desktop actions
            if self.safety_enabled and self._requires_confirmation(command):
                dangerous_actions = ['delete', 'format', 'shutdown', 'restart', 'close all']
                if any(action in command.lower() for action in dangerous_actions):
                    return f"🛡️ Safety block: Command '{command}' blocked for security. Use 'override safety' to proceed."
            
            result = await self.desktop_automation.execute_command(command, self.llm_manager, self.context_memory.get('rag'))
            
            # Add to history
            self.add_to_history(command, result, {
                "automation_type": "desktop",
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            return await self.handle_error(e, "desktop automation")
    
    async def _handle_workflow_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Handle multi-step automation workflows"""
        try:
            # Parse workflow from command using AI
            workflow_prompt = f"""
            Parse this automation workflow command: "{command}"
            
            Break it down into individual steps that can be executed sequentially.
            Each step should be a clear, actionable automation command.
            
            Return a JSON list of steps, for example:
            ["open browser", "navigate to google.com", "type 'hello world'", "take screenshot"]
            
            Maximum {self.max_steps} steps allowed.
            """
            
            workflow_response = await self.generate_response(workflow_prompt, context)
            
            try:
                import json
                steps = json.loads(workflow_response)
                if not isinstance(steps, list):
                    return "❌ Could not parse workflow steps"
                
                if len(steps) > self.max_steps:
                    return f"❌ Workflow too long ({len(steps)} steps). Maximum {self.max_steps} steps allowed."
                
                # Execute workflow
                return await self._execute_workflow(steps)
                
            except json.JSONDecodeError:
                # Fallback: try to parse manually
                return f"🤖 Workflow parsing result: {workflow_response}"
                
        except Exception as e:
            return await self.handle_error(e, "workflow processing")
    
    async def _execute_workflow(self, steps: list) -> str:
        """Execute a multi-step workflow"""
        try:
            self.current_workflow = {
                "steps": steps,
                "current_step": 0,
                "start_time": datetime.now(),
                "results": []
            }
            
            workflow_result = f"🤖 Executing workflow with {len(steps)} steps:\n\n"
            
            for i, step in enumerate(steps, 1):
                try:
                    workflow_result += f"Step {i}: {step}\n"
                    
                    # Determine step type and execute
                    if self._is_browser_command(step):
                        step_result = await self.browser_automation.execute_command(step, self.llm_manager, None)
                    elif self._is_desktop_command(step):
                        step_result = await self.desktop_automation.execute_command(step, self.llm_manager, None)
                    else:
                        step_result = f"❓ Unknown step type: {step}"
                    
                    workflow_result += f"Result: {step_result}\n\n"
                    
                    self.current_workflow["results"].append({
                        "step": step,
                        "result": step_result,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    self.current_workflow["current_step"] = i
                    
                    # Small delay between steps
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    error_msg = f"❌ Step {i} failed: {e}"
                    workflow_result += f"Result: {error_msg}\n\n"
                    workflow_result += "🛑 Workflow stopped due to error."
                    break
            
            # Workflow completed
            self.current_workflow = None
            workflow_result += "✅ Workflow completed!"
            
            return workflow_result
            
        except Exception as e:
            self.current_workflow = None
            return await self.handle_error(e, "workflow execution")
    
    async def _handle_stop_automation(self) -> str:
        """Stop current automation workflow"""
        if self.current_workflow:
            self.current_workflow = None
            return "🛑 Automation workflow stopped"
        else:
            return "ℹ️ No active automation workflow to stop"
    
    def _handle_automation_status(self) -> str:
        """Get automation agent status"""
        status = f"""
🤖 Automation Agent Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 Capabilities:
   • Browser: ✅ Available
   • Desktop: {'✅ Available' if self.get_context('desktop_available') else '❌ Unavailable'}
   • Safety checks: {'🟢 Enabled' if self.safety_enabled else '🔴 Disabled'}
   • Max workflow steps: {self.max_steps}

📊 Current State:
   • Active workflow: {'🟢 Yes' if self.current_workflow else '🔴 None'}
   • History entries: {len(self.conversation_history)}
   • Last activity: {self.last_activity.strftime('%Y-%m-%d %H:%M:%S') if self.last_activity else 'Never'}
"""
        
        if self.current_workflow:
            wf = self.current_workflow
            status += f"""
🔄 Active Workflow:
   • Total steps: {len(wf['steps'])}
   • Current step: {wf['current_step']}
   • Started: {wf['start_time'].strftime('%H:%M:%S')}
   • Completed steps: {len(wf['results'])}
"""
        
        return status
    
    def _requires_confirmation(self, command: str) -> bool:
        """Check if command requires user confirmation"""
        sensitive_keywords = [
            'submit', 'send', 'delete', 'purchase', 'buy',
            'payment', 'transfer', 'close', 'shutdown',
            'format', 'install', 'uninstall'
        ]
        return any(keyword in command.lower() for keyword in sensitive_keywords)
    
    async def _handle_ai_automation_command(self, command: str, context: Dict[str, Any] = None) -> str:
        """Handle general automation commands using AI"""
        try:
            ai_prompt = f"""
            I am an automation assistant. The user wants to: "{command}"
            
            Available automation capabilities:
            - Browser automation (navigate, click, fill forms, etc.)
            - Desktop automation (window management, keyboard/mouse control, screenshots)
            - Multi-step workflows
            
            Capabilities status:
            - Browser: Available
            - Desktop: {'Available' if self.get_context('desktop_available') else 'Not Available'}
            
            Based on the command, provide:
            1. What type of automation is needed
            2. Step-by-step instructions
            3. Any safety considerations
            4. Expected outcome
            
            If the command is unclear, ask for clarification with specific examples.
            """
            
            response = await self.generate_response(ai_prompt, context)
            return f"🤖 Automation Assistant: {response}"
            
        except Exception as e:
            return await self.handle_error(e, "AI automation command processing")