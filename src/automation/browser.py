# New file for browser control
import logging
from selenium import webdriver

logger = logging.getLogger(__name__)

from src.pipelines.handlers import BaseHandler

class BrowserHandler(BaseHandler):
    def __init__(self, intent="browser_control"):
        super().__init__()
        self.intent = intent
        self.driver = webdriver.Chrome()  # Assume Chrome, make configurable

    def can_handle(self, intent, entities, context):
        return intent == self.intent or "url" in entities or context.get("active_app", "").lower() == "chrome"

    def handle(self, command, intent, entities, context):
        if "search" in command.lower():
            query = entities.get("query", command.split("search for")[1])
            self.driver.get(f"https://www.google.com/search?q={query}")
            return f"Searched for {query}"
        elif "open" in command.lower():
            url = entities.get("url")
            self.driver.get(url)
            return f"Opened {url}"
        return "Browser action executed"