# New file for GUI actions
import logging
from pywinauto import Application

logger = logging.getLogger(__name__)

from src.pipelines.handlers import BaseHandler

class GUIActionsHandler(BaseHandler):
    def __init__(self, intent="gui_actions"):
        super().__init__()
        self.intent = intent

    def can_handle(self, intent, entities, context):
        return intent == self.intent or "click" in intent or "type" in intent

    def handle(self, command, intent, entities, context):
        app_name = context.get("active_app")
        app = Application().connect(title=app_name)
        if "click" in command:
            button = entities.get("button")
            app.top_window().child_window(title=button).click()
            return f"Clicked {button}"
        # Add more GUI actions
        return "GUI action executed"