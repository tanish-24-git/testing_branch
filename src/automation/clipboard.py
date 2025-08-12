# New file for clipboard
import logging
import pyperclip

logger = logging.getLogger(__name__)

from src.pipelines.handlers import BaseHandler

class ClipboardHandler(BaseHandler):
    def __init__(self, intent="clipboard"):
        super().__init__()
        self.intent = intent

    def can_handle(self, intent, entities, context):
        return intent == self.intent or "copy" in intent or "paste" in intent

    def handle(self, command, intent, entities, context):
        if "copy" in command.lower():
            text = entities.get("text", context.get("screen_content"))
            pyperclip.copy(text)
            return "Copied to clipboard"
        elif "paste" in command.lower():
            text = pyperclip.paste()
            # Assume paste into active app (placeholder)
            return f"Pasted: {text}"
        return "Clipboard action executed"