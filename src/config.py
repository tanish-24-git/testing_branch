import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_path="config.yaml"):
        try:
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
            logger.info("Configuration loaded")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.config = {}

    def get(self, key, default=None):
        return self.config.get(key, default)

config = Config()