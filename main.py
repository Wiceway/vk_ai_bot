#!/usr/bin/env python3
"""
VK AI Bot - AI-powered chatbot for VK conversations.

This bot can be added to VK conversations and configured to respond
with AI-generated messages based on customizable personality and settings.
"""

import asyncio
import logging
from vkbottle.bot import Bot

from config.config import Config
from database.db import Database
from bot.ai import AIManager
from bot.handlers import MessageHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the bot."""
    try:
        # Validate configuration
        Config.validate()
        logger.info("Configuration validated successfully")

        # Initialize database
        db = Database(Config.DB_PATH)
        await db.init_db()
        logger.info("Database initialized successfully")

        # Initialize AI manager
        ai = AIManager(Config.OPENAI_API_KEY, Config.OPENAI_MODEL)
        logger.info("AI manager initialized successfully")

        # Initialize bot
        bot = Bot(token=Config.VK_TOKEN)
        logger.info("Bot initialized successfully")

        # Register handlers
        handler = MessageHandler(bot, db, ai)
        handler.register_handlers()
        logger.info("Message handlers registered successfully")

        # Start bot
        logger.info("Starting bot...")
        await bot.run_polling()

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set.")
        raise
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
