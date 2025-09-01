
# FILE: src/agents/browser/browser_agent.py
# Orchestrates browser-related tasks by classifying intent and routing to handlers.
# Converts handler results to markdown strings for easy rendering in chat.

import logging
from typing import Dict
from ..base_agent import BaseAgent
from .intent_classifier import classify_intent
from .search_handler import handle_search
from .direct_handler import handle_direct
from .download_handler import handle_download
from .summarizer_handler import handle_summarize

logger = logging.getLogger(__name__)

class BrowserAgent(BaseAgent):
    def __init__(self, llm_manager, config: Dict):
        super().__init__("browser", llm_manager, config)

    async def process_command(self, command: str, context: Dict = None) -> str:
        """
        Processes the browser command by classifying intent and routing to the appropriate handler.
        Returns markdown string for frontend rendering.
        """
        intent = await classify_intent(self.llm_manager, command)
        logger.info(f"Classified intent: {intent} for command: {command}")

        if intent == "search":
            result = await handle_search(command)
        elif intent == "open_site":
            result = await handle_direct(command)
        elif intent == "download":
            result = await handle_download(self.llm_manager, command)
        elif intent == "summarize":
            result = await handle_summarize(self.llm_manager, command)
        else:
            return "Unknown intent"

        # Convert dict to markdown
        if 'error' in result:
            return f"Error: {result['error']}"
        elif 'results' in result:
            md = ""
            for r in result['results']:
                md += f"* [{r['title']}]({r['href']}): {r['body']}\n"
            return md
        elif 'url' in result:
            return f"Open site: [{result['url']}]({result['url']})"
        elif 'download_url' in result:
            return f"Download link: [{result['download_url']}]({result['download_url']})\n\nInstallation steps:\n{result['steps']}"
        elif 'summary' in result:
            return result['summary']
        return "Unknown response"