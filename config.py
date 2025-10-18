"""
Configuration settings for Discord-Poe-POC
"""
import os
from typing import List

class Config:
    """Bot configuration class"""
    
    # Discord settings
    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", "")
    COMMAND_PREFIX = os.environ.get("COMMAND_PREFIX", "!")
    
    # Poe API settings
    POE_API_KEY = os.environ.get("POE_API_KEY", "")
    POE_BASE_URL = "https://api.poe.com/v1"
    DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "Claude-Sonnet-4")
    
    # Bot behavior settings
    IGNORE_PREFIXES = ["!", "?", "/"]
    ALLOWED_CHANNELS = os.environ.get("ALLOWED_CHANNELS", "663843965325410319").split(",")
    MAX_RESPONSE_LENGTH = 2000
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
    
    # System message for AI
    SYSTEM_MESSAGE = os.environ.get(
        "SYSTEM_MESSAGE", 
        "You are a helpful Discord bot assistant. Be concise and friendly."
    )
    
    # Modal deployment settings
    MODAL_APP_NAME = "discord-poe-poc"
    KEEP_WARM = 1
    TIMEOUT = 3600  # 1 hour
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate required configuration values"""
        errors = []
        
        if not cls.DISCORD_TOKEN:
            errors.append("DISCORD_TOKEN is required")
        
        if not cls.POE_API_KEY:
            errors.append("POE_API_KEY is required")
        
        return errors

# Available Poe models for reference
AVAILABLE_MODELS = [
    "Claude-Sonnet-4",
    "Claude-Opus-4.1", 
    "GPT-4.1",
    "Gemini-2.5-Pro",
    "Llama-3.1-405B",
    "Grok-4",
    # Add more as they become available
]