# src/automation/browser.py
import logging
import webbrowser

logger = logging.getLogger(__name__)

from src.pipelines.handlers import BaseHandler

class BrowserHandler(BaseHandler):
    def __init__(self, intent="browser_control"):
        super().__init__()
        self.intent = intent

    def can_handle(self, intent, entities, context):
        return intent == self.intent or "url" in entities or context.get("active_app", "").lower() in ["chrome", "edge", "firefox"]

    def handle(self, command, intent, entities, context):
        if "search" in command.lower():
            query = entities.get("query", command.split("search for")[-1].strip())
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return f"Searched for {query}"
        elif "open" in command.lower() and "url" in entities:
            url = entities.get("url")
            webbrowser.open(url)
            return f"Opened {url}"
        return "Browser action executed"