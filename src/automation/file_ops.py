# src/automation/file_ops.py
import logging
import os
import shutil
import platform
import subprocess

logger = logging.getLogger(__name__)

from src.pipelines.handlers import BaseHandler

class FileOpsHandler(BaseHandler):
    def __init__(self, intent="file_ops"):
        super().__init__()
        self.intent = intent

    def can_handle(self, intent, entities, context):
        return intent == self.intent or "file" in entities or context.get("file_type")

    def handle(self, command, intent, entities, context):
        file_path = entities.get("file")
        if "open" in command:
            os.startfile(file_path) if platform.system() == "Windows" else subprocess.run(["open", file_path]) if platform.system() == "Darwin" else subprocess.run(["xdg-open", file_path])
            return f"Opened file {file_path}"
        elif "copy" in command:
            dest = entities.get("dest")
            shutil.copy(file_path, dest)
            return f"Copied file to {dest}"
        # Add more ops
        return "File operation executed"