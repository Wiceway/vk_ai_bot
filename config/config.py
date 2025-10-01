import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    VK_TOKEN = os.getenv("VK_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    DB_PATH = os.getenv("DB_PATH", "bot_data.db")

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.VK_TOKEN:
            raise ValueError("VK_TOKEN is not set in environment variables")
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in environment variables")
