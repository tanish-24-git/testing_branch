import logging
from playwright.async_api import async_playwright, Playwright, Browser
from src.config import config
import asyncio
import re

logger = logging.getLogger(__name__)

class ChromeAutomation:
    def __init__(self):
        self.browser: Browser = None
        self.page = None
        self.playwright = None
        self.headless = config.get("automation", {}).get("headless", True)
        self.timeout = config.get("automation", {}).get("timeout", 30000)

    async def start_browser(self):
        logger.info("Attempting to start browser")
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            context = await self.browser.new_context()
            self.page = await context.new_page()
            await self.page.set_default_timeout(self.timeout)
            logger.info("Browser started successfully")
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            self.page = None
            self.browser = None
            self.playwright = None
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
            return f"Navigated to {url}"
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

    async def execute_command(self, command: str, llm_manager, rag):
        if not self.page:
            try:
                await self.start_browser()
            except Exception as e:
                return f"Failed to initialize browser: {str(e)}"
        try:
            # Use LLM to parse command
            context = {"rag": rag.retrieve(command)}
            parsed = await llm_manager.process(f"Parse automation command: {command}", context)
            logger.info(f"Parsed command: {parsed}")

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
            else:
                return f"Unknown command: {command}"
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return f"Error executing command: {str(e)}"
        finally:
            await self.close_browser()