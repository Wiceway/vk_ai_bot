from vkbottle.bot import Message
from database.db import Database
import re


class AdminCommands:
    """Handler for admin commands."""

    def __init__(self, db: Database):
        self.db = db

    async def handle_command(self, message: Message, command: str, args: str) -> str:
        """Route and handle admin commands."""
        peer_id = message.peer_id
        user_id = message.from_id

        # Check if user is admin (except for first initialization)
        is_admin = await self.db.is_admin(peer_id, user_id)

        # Command handlers
        if command == "помощь" or command == "help":
            return self._help_message(is_admin)

        if command == "команды":
            return self._help_message(is_admin)

        # Admin-only commands
        if not is_admin:
            return "❌ Эта команда доступна только администраторам бота."

        if command == "добавить_админа":
            return await self._add_admin(peer_id, args)

        elif command == "удалить_админа":
            return await self._remove_admin(peer_id, args)

        elif command == "список_админов":
            return await self._list_admins(peer_id)

        elif command == "установить_роль":
            return await self._set_brain_role(peer_id, args)

        elif command == "установить_задачу":
            return await self._set_brain_task(peer_id, args)

        elif command == "установить_мозги":
            return await self._set_brain_combined(peer_id, args)

        elif command == "длина_ответов":
            return await self._set_response_length(peer_id, args)

        elif command == "процент_ответов":
            return await self._set_response_percentage(peer_id, args)

        elif command == "размер_памяти":
            return await self._set_memory_size(peer_id, args)

        elif command == "добавить_пользователя":
            return await self._add_tracked_user(peer_id, args)

        elif command == "удалить_пользователя":
            return await self._remove_tracked_user(peer_id, args)

        elif command == "список_пользователей":
            return await self._list_tracked_users(peer_id)

        elif command == "статус":
            return await self._show_status(peer_id)

        return "❓ Неизвестная команда. Используйте !помощь для списка команд."

    def _help_message(self, is_admin: bool) -> str:
        """Generate help message."""
        base_help = """
🤖 **Команды бота:**

**Общие команды:**
!помощь - показать это сообщение
!команды - показать это сообщение
!статус - показать текущие настройки бота
"""

        if not is_admin:
            return base_help + "\n❗ Для доступа к настройкам нужны права администратора."

        admin_help = """
**Управление администраторами:**
!добавить_админа [id] - добавить администратора
!удалить_админа [id] - удалить администратора
!список_админов - показать всех админов

**Настройка "мозгов":**
!установить_роль [текст] - задать роль бота
!установить_задачу [текст] - задать задачу бота
!установить_мозги [роль] | [задача] - задать роль и задачу одной командой

**Настройки ответов:**
!длина_ответов [short/medium/long] - длина ответов
!процент_ответов [1-100] - процент ответов на сообщения
!размер_памяти [число] - количество запоминаемых сообщений

**Управление пользователями:**
!добавить_пользователя [id] - добавить пользователя для отслеживания
!удалить_пользователя [id] - удалить пользователя
!список_пользователей - показать отслеживаемых пользователей

**Примеры:**
!установить_роль Я водитель грузовика с 20-летним стажем
!установить_задачу Я пишу здесь, чтобы скоротать время за рулем
!длина_ответов medium
!процент_ответов 50
!добавить_пользователя 123456789
"""
        return base_help + admin_help

    async def _add_admin(self, peer_id: int, args: str) -> str:
        """Add admin."""
        match = re.search(r'\[id(\d+)\|', args) or re.search(r'id(\d+)', args) or re.search(r'(\d+)', args)
        if not match:
            return "❌ Укажите ID пользователя. Пример: !добавить_админа 123456789"

        user_id = int(match.group(1))
        await self.db.add_admin(peer_id, user_id)
        return f"✅ Пользователь [id{user_id}|@id{user_id}] добавлен в администраторы."

    async def _remove_admin(self, peer_id: int, args: str) -> str:
        """Remove admin."""
        match = re.search(r'\[id(\d+)\|', args) or re.search(r'id(\d+)', args) or re.search(r'(\d+)', args)
        if not match:
            return "❌ Укажите ID пользователя. Пример: !удалить_админа 123456789"

        user_id = int(match.group(1))
        await self.db.remove_admin(peer_id, user_id)
        return f"✅ Пользователь [id{user_id}|@id{user_id}] удален из администраторов."

    async def _list_admins(self, peer_id: int) -> str:
        """List admins."""
        config = await self.db.get_or_create_conversation(peer_id, 0)
        import json
        admins = json.loads(config['admins'])

        if not admins:
            return "📋 Администраторы не назначены."

        admin_list = "\n".join([f"- [id{uid}|@id{uid}]" for uid in admins])
        return f"📋 **Администраторы беседы:**\n{admin_list}"

    async def _set_brain_role(self, peer_id: int, args: str) -> str:
        """Set brain role."""
        if not args.strip():
            return "❌ Укажите роль. Пример: !установить_роль Я водитель грузовика"

        await self.db.update_conversation(peer_id, brain_role=args.strip())
        return f"✅ Роль бота установлена: {args.strip()}"

    async def _set_brain_task(self, peer_id: int, args: str) -> str:
        """Set brain task."""
        if not args.strip():
            return "❌ Укажите задачу. Пример: !установить_задачу Скоротать время за рулем"

        await self.db.update_conversation(peer_id, brain_task=args.strip())
        return f"✅ Задача бота установлена: {args.strip()}"

    async def _set_brain_combined(self, peer_id: int, args: str) -> str:
        """Set brain role and task together."""
        if '|' not in args:
            return "❌ Разделите роль и задачу символом |. Пример: !установить_мозги Водитель грузовика | Скоротать время"

        parts = args.split('|', 1)
        role = parts[0].strip()
        task = parts[1].strip()

        await self.db.update_conversation(peer_id, brain_role=role, brain_task=task)
        return f"✅ Установлено:\nРоль: {role}\nЗадача: {task}"

    async def _set_response_length(self, peer_id: int, args: str) -> str:
        """Set response length."""
        length = args.strip().lower()
        if length not in ['short', 'medium', 'long']:
            return "❌ Допустимые значения: short, medium, long"

        await self.db.update_conversation(peer_id, response_length=length)
        return f"✅ Длина ответов установлена: {length}"

    async def _set_response_percentage(self, peer_id: int, args: str) -> str:
        """Set response percentage."""
        try:
            percentage = int(args.strip())
            if not 1 <= percentage <= 100:
                raise ValueError
        except ValueError:
            return "❌ Укажите число от 1 до 100"

        await self.db.update_conversation(peer_id, response_percentage=percentage)
        return f"✅ Процент ответов установлен: {percentage}%"

    async def _set_memory_size(self, peer_id: int, args: str) -> str:
        """Set memory size."""
        try:
            size = int(args.strip())
            if size < 1:
                raise ValueError
        except ValueError:
            return "❌ Укажите положительное число"

        await self.db.update_conversation(peer_id, memory_size=size)
        return f"✅ Размер памяти установлен: {size} сообщений"

    async def _add_tracked_user(self, peer_id: int, args: str) -> str:
        """Add tracked user."""
        match = re.search(r'\[id(\d+)\|', args) or re.search(r'id(\d+)', args) or re.search(r'(\d+)', args)
        if not match:
            return "❌ Укажите ID пользователя. Пример: !добавить_пользователя 123456789"

        user_id = int(match.group(1))
        await self.db.add_tracked_user(peer_id, user_id)
        return f"✅ Пользователь [id{user_id}|@id{user_id}] добавлен в список отслеживания."

    async def _remove_tracked_user(self, peer_id: int, args: str) -> str:
        """Remove tracked user."""
        match = re.search(r'\[id(\d+)\|', args) or re.search(r'id(\d+)', args) or re.search(r'(\d+)', args)
        if not match:
            return "❌ Укажите ID пользователя. Пример: !удалить_пользователя 123456789"

        user_id = int(match.group(1))
        await self.db.remove_tracked_user(peer_id, user_id)
        return f"✅ Пользователь [id{user_id}|@id{user_id}] удален из списка отслеживания."

    async def _list_tracked_users(self, peer_id: int) -> str:
        """List tracked users."""
        users = await self.db.get_tracked_users(peer_id)

        if not users:
            return "📋 Нет отслеживаемых пользователей. Используйте !добавить_пользователя"

        user_list = "\n".join([f"- [id{uid}|@id{uid}]" for uid in users])
        return f"📋 **Отслеживаемые пользователи:**\n{user_list}"

    async def _show_status(self, peer_id: int) -> str:
        """Show current bot configuration."""
        config = await self.db.get_or_create_conversation(peer_id, 0)
        import json

        admins = json.loads(config['admins'])
        tracked_users = await self.db.get_tracked_users(peer_id)

        status = f"""📊 **Текущие настройки бота:**

**Роль:** {config.get('brain_role') or 'Не установлена'}
**Задача:** {config.get('brain_task') or 'Не установлена'}
**Длина ответов:** {config.get('response_length', 'medium')}
**Процент ответов:** {config.get('response_percentage', 100)}%
**Размер памяти:** {config.get('memory_size', 10)} сообщений
**Количество админов:** {len(admins)}
**Отслеживаемых пользователей:** {len(tracked_users)}
"""
        return status
