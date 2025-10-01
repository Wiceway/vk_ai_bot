from vkbottle.bot import Bot, Message
from vkbottle import BaseStateGroup
from database.db import Database
from bot.ai import AIManager
from bot.admin import AdminCommands
import random
import logging

logger = logging.getLogger(__name__)


class MessageHandler:
    """Main message handler for the bot."""

    def __init__(self, bot: Bot, db: Database, ai: AIManager):
        self.bot = bot
        self.db = db
        self.ai = ai
        self.admin_commands = AdminCommands(db)

    def register_handlers(self):
        """Register all message handlers."""

        @self.bot.on.message()
        async def handle_message(message: Message):
            """Handle all incoming messages."""
            try:
                # Ignore messages from the bot itself
                if message.from_id < 0:
                    return

                peer_id = message.peer_id
                user_id = message.from_id
                text = message.text

                # Initialize conversation if not exists (first message sets sender as admin)
                config = await self.db.get_or_create_conversation(peer_id, user_id)

                # Check for admin commands (start with !)
                if text and text.startswith('!'):
                    parts = text[1:].split(maxsplit=1)
                    command = parts[0].lower()
                    args = parts[1] if len(parts) > 1 else ""

                    response = await self.admin_commands.handle_command(message, command, args)
                    await message.answer(response)
                    return

                # Check if we should respond to this message
                should_respond = await self._should_respond(peer_id, user_id, config)

                if not should_respond:
                    # Still save to history for context
                    await self.db.add_message_to_history(peer_id, user_id, text, is_bot=False)
                    return

                # Get conversation history
                history = await self.db.get_conversation_history(
                    peer_id,
                    limit=config.get('memory_size', 10)
                )

                # Add current message to history context
                history.append({
                    'user_id': user_id,
                    'message': text,
                    'is_bot': False
                })

                # Generate AI response
                response = await self.ai.generate_response(
                    brain_role=config.get('brain_role'),
                    brain_task=config.get('brain_task'),
                    conversation_history=history,
                    response_length=config.get('response_length', 'medium')
                )

                # Send response
                await message.answer(response)

                # Save messages to history
                await self.db.add_message_to_history(peer_id, user_id, text, is_bot=False)
                await self.db.add_message_to_history(peer_id, -1, response, is_bot=True)

                # Clean old history if needed
                await self.db.clear_old_history(peer_id, keep_last=config.get('memory_size', 10) * 2)

            except Exception as e:
                logger.error(f"Error handling message: {e}", exc_info=True)
                try:
                    await message.answer("❌ Произошла ошибка при обработке сообщения.")
                except:
                    pass

    async def _should_respond(self, peer_id: int, user_id: int, config: dict) -> bool:
        """Determine if bot should respond to this message."""

        # Check if there are tracked users
        tracked_users = await self.db.get_tracked_users(peer_id)

        # If no tracked users, don't respond (admin needs to configure first)
        if not tracked_users:
            return False

        # Check if user is in tracked list
        if user_id not in tracked_users:
            return False

        # Check response percentage
        response_percentage = config.get('response_percentage', 100)
        if response_percentage < 100:
            # Random chance based on percentage
            return random.randint(1, 100) <= response_percentage

        return True
