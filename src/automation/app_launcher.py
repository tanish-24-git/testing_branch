# src/automation/app_launcher.py
import logging
import subprocess
import platform

logger = logging.getLogger(__name__)

from src.pipelines.handlers import BaseHandler

class AppLauncherHandler(BaseHandler):
    def __init__(self, intent="open_app"):
        super().__init__()
        self.intent = intent
        self.command_map = {  # Cross-platform commands
            "chrome": "google-chrome" if platform.system() != "Windows" else "start chrome",
            "notepad": "gedit" if platform.system() == "Linux" else "notepad" if platform.system() == "Windows" else "open -a TextEdit"
        }

    def can_handle(self, intent, entities, context):
        return intent == self.intent and "app" in entities

    def handle(self, command, intent, entities, context):
        app = entities.get("app")
        cmd = self.command_map.get(app.lower())
        if cmd:
            subprocess.run(cmd, shell=True)
            return f"Launched {app}"
        return "App not found"