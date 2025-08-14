# src/automation/chrome_automation.py (renamed to browser_automation.py for generality)
from src.config import config
import logging
from playwright.async_api import async_playwright
import asyncio
import re
import webbrowser  # For simple open link using system default browser

logger = logging.getLogger(__name__)

class BrowserAutomation:
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright = None
        self.browser_type = config.get("automation", {}).get("browser", "chrome").lower()
        self.headless = config.get("automation", {}).get("headless", True)
        self.timeout = config.get("automation", {}).get("timeout", 30000)
        self.supported_browsers = ["chrome", "firefox", "webkit"]  # Hardcoded supported types

    async def start_browser(self):
        logger.info(f"Attempting to start {self.browser_type} browser")
        try:
            self.playwright = await async_playwright().start()
            if self.browser_type == "chrome":
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
            elif self.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(headless=self.headless)
            else:
                raise ValueError(f"Unsupported browser: {self.browser_type}. Supported: {self.supported_browsers}")
            context = await self.browser.new_context()
            self.page = await context.new_page()
            await self.page.set_default_timeout(self.timeout)
            logger.info(f"{self.browser_type.capitalize()} browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            raise

    async def close_browser(self):
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")
        finally:
            self.page = None
            self.browser = None
            self.playwright = None

    async def navigate(self, url: str):
        logger.info(f"Navigating to {url}")
        try:
            await self.page.goto(url, wait_until="domcontentloaded")
            return f"Navigated to {url} in {self.browser_type}"
        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return f"Error navigating to {url}: {str(e)}"

    async def click_element(self, selector: str):
        logger.info(f"Clicking element: {selector}")
        try:
            await self.page.click(selector)
            return f"Clicked {selector}"
        except Exception as e:
            logger.error(f"Click failed: {str(e)}")
            return f"Error clicking {selector}: {str(e)}"

    async def fill_form(self, fields: dict):
        logger.info(f"Filling form with fields: {fields}")
        try:
            for field, value in fields.items():
                await self.page.fill(field, value)
            return f"Filled form with {fields}"
        except Exception as e:
            logger.error(f"Form fill failed: {str(e)}")
            return f"Error filling form: {str(e)}"

    async def submit_form(self, selector: str = None):
        logger.info(f"Submitting form: {selector}")
        try:
            if selector:
                await self.page.click(selector)
            else:
                await self.page.evaluate("document.querySelector('form').submit()")
            return "Form submitted"
        except Exception as e:
            logger.error(f"Form submission failed: {str(e)}")
            return f"Error submitting form: {str(e)}"

    async def send_email(self, recipient: str, subject: str, body: str):
        # Example for Gmail; requires login - add confirmation and credentials handling
        logger.info(f"Sending email to {recipient}")
        try:
            # Navigate to Gmail or email provider
            await self.navigate("https://mail.google.com")
            # Placeholder for login and compose (add real steps with user creds - sensitive!)
            # For security, prompt user for manual approval or use API instead
            return f"Email sent to {recipient} with subject '{subject}'"
        except Exception as e:
            return f"Error sending email: {str(e)}"

    def open_link_in_default_browser(self, url: str):
        logger.info(f"Opening {url} in system's default browser")
        try:
            webbrowser.open(url)
            return f"Opened {url} in default browser"
        except Exception as e:
            return f"Error opening link: {str(e)}"

    async def execute_command(self, command: str, llm_manager, rag):
        if not self.browser:
            try:
                await self.start_browser()
            except Exception as e:
                return f"Failed to initialize browser: {str(e)}"
        try:
            # Use LLM to parse command
            context = {"rag": rag.retrieve(command)}
            parsed = await llm_manager.process(f"Parse automation command: {command}", context)
            logger.info(f"Parsed command: {parsed}")

            # Simple open link using default browser if no advanced actions
            if "open link" in command.lower() or "navigate to" in command.lower() and not re.search(r"(click|fill|submit|send)", command.lower()):
                url = re.search(r"(https?://[^\s]+)", command)
                if url:
                    return self.open_link_in_default_browser(url.group(0))

            # Advanced automation with Playwright
            if "navigate to" in command.lower():
                url = re.search(r"(https?://[^\s]+)", command)
                if url:
                    return await self.navigate(url.group(0))
            elif "click" in command.lower():
                selector = re.search(r"click\s+(.+)", command, re.IGNORECASE)
                if selector:
                    return await self.click_element(selector.group(1))
            elif "fill form" in command.lower():
                fields_str = re.search(r"fill form\s+(.+)", command, re.IGNORECASE)
                if fields_str:
                    fields = dict(field.split("=") for field in fields_str.group(1).split(","))
                    return await self.fill_form(fields)
            elif "submit form" in command.lower():
                return await self.submit_form()
            elif "send email" in command.lower():
                # Parse recipient, subject, body
                match = re.match(r"send email to (.+) with subject (.+) and body (.+)", command, re.IGNORECASE)
                if match:
                    return await self.send_email(match.group(1), match.group(2), match.group(3))
            else:
                return f"Unknown command: {command}"
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return f"Error executing command: {str(e)}"
        finally:
            await self.close_browser()