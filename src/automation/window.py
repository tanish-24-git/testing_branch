# src/automation/window.py
import logging
import platform
import subprocess
from pywinauto import Application
from src.pipelines.handlers import BaseHandler

logger = logging.getLogger(__name__)

class WindowHandler(BaseHandler):
    def __init__(self, intent="window_management"):
        super().__init__()
        self.intent = intent

    def can_handle(self, intent, entities, context):
        return intent == self.intent or "window" in intent.lower() or any(keyword in intent.lower() for keyword in ["minimize", "maximize", "switch"])

    def handle(self, command, intent, entities, context):
        app_name = context.get("active_app", "Unknown Application")
        try:
            if platform.system() == "Windows":
                app = Application().connect(title=app_name)
                window = app.top_window()
                if "minimize" in command.lower():
                    window.minimize()
                    return f"Minimized {app_name}"
                elif "maximize" in command.lower():
                    window.maximize()
                    return f"Maximized {app_name}"
                elif "switch" in command.lower():
                    target = entities.get("app", app_name)
                    subprocess.run(f"start {target}", shell=True)
                    return f"Switched to {target}"
            elif platform.system() == "Darwin":
                if "minimize" in command.lower():
                    subprocess.run(["osascript", "-e", f'tell app "{app_name}" to set miniaturized of window 1 to true'])
                    return f"Minimized {app_name}"
                elif "maximize" in command.lower():
                    subprocess.run(["osascript", "-e", f'tell app "{app_name}" to set bounds of window 1 to {{0, 0, 1280, 720}}'])
                    return f"Maximized {app_name}"
                elif "switch" in command.lower():
                    target = entities.get("app", app_name)
                    subprocess.run(["open", "-a", target])
                    return f"Switched to {target}"
            elif platform.system() == "Linux":
                logger.warning("Linux window management not fully implemented")
                return "Window management not supported on Linux yet"
            return "Window action executed"
        except Exception as e:
            logger.error(f"Window management error: {e}")
            return f"Error performing window action: {str(e)}"