# New file for base handler in chain-of-responsibility
import logging

logger = logging.getLogger(__name__)

class BaseHandler:
    def __init__(self):
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler
        return handler

    def can_handle(self, intent, entities, context):
        raise NotImplementedError("Subclasses must implement can_handle")

    def handle(self, command, intent, entities, context):
        if self.next_handler:
            return self.next_handler.handle(command, intent, entities, context)
        return "No handler found"