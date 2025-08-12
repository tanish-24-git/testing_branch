import yaml
import logging
from pathlib import Path
import importlib

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_path="config.yaml"):
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = {}

    def get(self, key, default=None):
        """Get configuration value by key."""
        return self.config.get(key, default)

    def get_handlers(self):
        """Dynamically load handlers from config."""
        handlers = []
        for intent, handler_path in self.config.get('handlers', {}).items():
            module_name, class_name = handler_path.rsplit('.', 1)
            module = importlib.import_module(module_name)
            handler_class = getattr(module, class_name)
            handlers.append(handler_class(intent=intent))
        return handlers

config = Config()