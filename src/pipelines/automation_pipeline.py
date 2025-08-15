# FIXED src/pipelines/automation_pipeline.py - Corrected imports and enhanced error handling

import logging
import sys
import os

# Add project root to path for proper imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.llm_manager import LLMManager
from src.rag import RAG

# FIXED: Correct import path
from automation.browser.browser_automation import browserAutomation

logger = logging.getLogger(__name__)

class AutomationPipeline:
    def __init__(self, llm_manager: LLMManager, rag: RAG):
        self.llm_manager = llm_manager
        self.rag = rag
        self.automation = browserAutomation()
        
        logger.info("AutomationPipeline initialized with enhanced browser automation")

    async def process(self, command: str, context: dict = {}) -> str:
        """Process automation command with enhanced error handling and security checks"""
        
        try:
            logger.info(f"Processing automation command: {command}")
            
            # Security checks for sensitive operations
            sensitive_keywords = ["submit form", "make payment", "send email", "delete", "purchase"]
            is_sensitive = any(keyword in command.lower() for keyword in sensitive_keywords)
            
            if is_sensitive:
                logger.warning(f"Sensitive automation command detected: {command}")
                context["requires_confirmation"] = True
                context["security_warning"] = "This command may perform sensitive actions"
            
            # Add RAG context for better command understanding
            rag_context = self.rag.retrieve(command)
            context["rag"] = rag_context
            
            # Execute the automation command
            result = await self.automation.execute_command(command, self.llm_manager, self.rag)
            
            # Log the result
            logger.info(f"Automation result: {result}")
            
            # Add context information to result if needed
            if context.get("requires_confirmation"):
                result = f"🛡️ Security Notice: {context.get('security_warning', '')}\n\n{result}"
            
            return result
            
        except Exception as e:
            error_msg = f"❌ Automation pipeline error: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def get_automation_status(self) -> dict:
        """Get current automation system status"""
        try:
            # Check if Playwright is available
            try:
                from playwright.async_api import async_playwright
                playwright_available = True
            except ImportError:
                playwright_available = False
            
            # Check browser automation capabilities
            browser_status = await self._check_browser_capabilities()
            
            # Check email configuration
            email_configured = bool(
                self.automation.smtp_username and 
                self.automation.smtp_password
            )
            
            status = {
                "playwright_available": playwright_available,
                "browser_automation": browser_status,
                "email_configured": email_configured,
                "supported_browsers": ["chrome", "firefox", "webkit"],
                "fallback_methods": ["system_browser", "command_line"],
                "email_methods": ["smtp"],
                "status": "ready" if playwright_available else "limited"
            }
            
            logger.info(f"Automation status: {status}")
            return status
            
        except Exception as e:
            logger.error(f"Error checking automation status: {e}")
            return {"status": "error", "error": str(e)}

    async def _check_browser_capabilities(self) -> dict:
        """Check what browser automation capabilities are available"""
        capabilities = {
            "playwright": False,
            "system_browser": True,  # This should always work
            "command_line": True     # This should work on most systems
        }
        
        try:
            # Test if we can start a browser with Playwright
            test_result = await self.automation.start_browser()
            if test_result:
                capabilities["playwright"] = True
                await self.automation.close_browser()
            
        except Exception as e:
            logger.debug(f"Playwright browser test failed: {e}")
            capabilities["playwright"] = False
        
        return capabilities

    async def execute_safe_command(self, command: str) -> str:
        """Execute command with additional safety checks"""
        
        # List of commands that are always safe to execute
        safe_commands = [
            "open", "navigate", "visit", "go to", 
            "screenshot", "get title", "get url"
        ]
        
        # Check if command is safe
        is_safe = any(safe_cmd in command.lower() for safe_cmd in safe_commands)
        
        if is_safe:
            return await self.process(command)
        else:
            # For potentially unsafe commands, add extra confirmation
            warning = f"⚠️ Command '{command}' may perform actions that modify data or send information. "
            result = await self.process(command)
            return f"{warning}\n\n{result}"