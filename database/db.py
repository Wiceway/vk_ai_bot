import aiosqlite
from typing import List, Optional, Dict, Any
from datetime import datetime


class Database:
    """Database manager for bot configuration and conversation history."""

    def __init__(self, db_path: str = "bot_data.db"):
        self.db_path = db_path

    async def init_db(self):
        """Initialize database with required tables."""
        async with aiosqlite.connect(self.db_path) as db:
            # Conversations table - stores bot configuration for each conversation
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    peer_id INTEGER PRIMARY KEY,
                    admins TEXT NOT NULL DEFAULT '[]',
                    brain_role TEXT,
                    brain_task TEXT,
                    response_length TEXT DEFAULT 'medium',
                    response_percentage INTEGER DEFAULT 100,
                    memory_size INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tracked users table - users whose messages the bot should respond to
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tracked_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    peer_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(peer_id, user_id),
                    FOREIGN KEY (peer_id) REFERENCES conversations(peer_id)
                )
            """)

            # Conversation history table - stores message history for context
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    peer_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    is_bot BOOLEAN DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (peer_id) REFERENCES conversations(peer_id)
                )
            """)

            # Create indexes for better performance
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_tracked_users_peer
                ON tracked_users(peer_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_peer
                ON conversation_history(peer_id, timestamp DESC)
            """)

            await db.commit()

    async def get_or_create_conversation(self, peer_id: int, admin_id: int) -> Dict[str, Any]:
        """Get conversation config or create if not exists."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            cursor = await db.execute(
                "SELECT * FROM conversations WHERE peer_id = ?",
                (peer_id,)
            )
            row = await cursor.fetchone()

            if row:
                return dict(row)

            # Create new conversation with admin as first admin
            await db.execute(
                """INSERT INTO conversations (peer_id, admins)
                   VALUES (?, ?)""",
                (peer_id, f'[{admin_id}]')
            )
            await db.commit()

            cursor = await db.execute(
                "SELECT * FROM conversations WHERE peer_id = ?",
                (peer_id,)
            )
            row = await cursor.fetchone()
            return dict(row)

    async def update_conversation(self, peer_id: int, **kwargs):
        """Update conversation configuration."""
        if not kwargs:
            return

        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [peer_id]

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                f"UPDATE conversations SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE peer_id = ?",
                values
            )
            await db.commit()

    async def add_admin(self, peer_id: int, user_id: int) -> bool:
        """Add admin to conversation."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT admins FROM conversations WHERE peer_id = ?",
                (peer_id,)
            )
            row = await cursor.fetchone()

            if not row:
                return False

            import json
            admins = json.loads(row[0])
            if user_id not in admins:
                admins.append(user_id)
                await db.execute(
                    "UPDATE conversations SET admins = ? WHERE peer_id = ?",
                    (json.dumps(admins), peer_id)
                )
                await db.commit()

            return True

    async def remove_admin(self, peer_id: int, user_id: int) -> bool:
        """Remove admin from conversation."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT admins FROM conversations WHERE peer_id = ?",
                (peer_id,)
            )
            row = await cursor.fetchone()

            if not row:
                return False

            import json
            admins = json.loads(row[0])
            if user_id in admins:
                admins.remove(user_id)
                await db.execute(
                    "UPDATE conversations SET admins = ? WHERE peer_id = ?",
                    (json.dumps(admins), peer_id)
                )
                await db.commit()

            return True

    async def is_admin(self, peer_id: int, user_id: int) -> bool:
        """Check if user is admin in conversation."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT admins FROM conversations WHERE peer_id = ?",
                (peer_id,)
            )
            row = await cursor.fetchone()

            if not row:
                return False

            import json
            admins = json.loads(row[0])
            return user_id in admins

    async def add_tracked_user(self, peer_id: int, user_id: int):
        """Add user to tracking list."""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    "INSERT INTO tracked_users (peer_id, user_id) VALUES (?, ?)",
                    (peer_id, user_id)
                )
                await db.commit()
            except aiosqlite.IntegrityError:
                pass  # Already exists

    async def remove_tracked_user(self, peer_id: int, user_id: int):
        """Remove user from tracking list."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM tracked_users WHERE peer_id = ? AND user_id = ?",
                (peer_id, user_id)
            )
            await db.commit()

    async def get_tracked_users(self, peer_id: int) -> List[int]:
        """Get list of tracked users for conversation."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT user_id FROM tracked_users WHERE peer_id = ?",
                (peer_id,)
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

    async def is_tracked_user(self, peer_id: int, user_id: int) -> bool:
        """Check if user is tracked."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT 1 FROM tracked_users WHERE peer_id = ? AND user_id = ?",
                (peer_id, user_id)
            )
            return await cursor.fetchone() is not None

    async def add_message_to_history(self, peer_id: int, user_id: int, message: str, is_bot: bool = False):
        """Add message to conversation history."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """INSERT INTO conversation_history (peer_id, user_id, message, is_bot)
                   VALUES (?, ?, ?, ?)""",
                (peer_id, user_id, message, is_bot)
            )
            await db.commit()

    async def get_conversation_history(self, peer_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT user_id, message, is_bot, timestamp
                   FROM conversation_history
                   WHERE peer_id = ?
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (peer_id, limit)
            )
            rows = await cursor.fetchall()
            # Return in chronological order (oldest first)
            return [dict(row) for row in reversed(rows)]

    async def clear_old_history(self, peer_id: int, keep_last: int = 10):
        """Clear old messages, keeping only the most recent ones."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """DELETE FROM conversation_history
                   WHERE peer_id = ?
                   AND id NOT IN (
                       SELECT id FROM conversation_history
                       WHERE peer_id = ?
                       ORDER BY timestamp DESC
                       LIMIT ?
                   )""",
                (peer_id, peer_id, keep_last)
            )
            await db.commit()
