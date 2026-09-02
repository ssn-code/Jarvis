import json
from typing import List, Optional
from app.services.database import db, DatabaseManager
from app.models.domain import AgentMessage, MessageRole


class ShortTermMemory:
    """Manages short-term context (conversation history) backed by the SQLite database."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or db

    async def add_message(self, message: AgentMessage, task_id: Optional[str] = None) -> None:
        """Saves a new AgentMessage into the database, optionally linking it to a task."""
        query = """
            INSERT INTO messages (task_id, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?);
        """
        params = (
            task_id,
            message.role.value,
            message.content,
            message.timestamp.isoformat(),
            json.dumps(message.metadata)
        )
        await self.db.execute(query, params)

    async def get_history(self, task_id: Optional[str] = None, limit: int = 50) -> List[AgentMessage]:
        """
        Retrieves the most recent message history.
        Returns the messages in chronological order (oldest first).
        """
        if task_id:
            query = """
                SELECT role, content, timestamp, metadata FROM messages
                WHERE task_id = ?
                ORDER BY id DESC
                LIMIT ?;
            """
            params = (task_id, limit)
        else:
            query = """
                SELECT role, content, timestamp, metadata FROM messages
                ORDER BY id DESC
                LIMIT ?;
            """
            params = (limit,)

        rows = await self.db.fetchall(query, params)
        # Reverse the list so it is in ascending chronological order
        rows.reverse()

        messages = []
        for row in rows:
            try:
                metadata = json.loads(row["metadata"])
            except (json.JSONDecodeError, TypeError):
                metadata = {}

            messages.append(AgentMessage(
                role=MessageRole(row["role"]),
                content=row["content"],
                timestamp=row["timestamp"],  # Pydantic will auto-parse ISO string to timezone-aware datetime
                metadata=metadata
            ))
        return messages

    async def clear_history(self, task_id: Optional[str] = None) -> None:
        """Deletes messages from the database, either globally or for a specific task."""
        if task_id:
            query = "DELETE FROM messages WHERE task_id = ?;"
            params = (task_id,)
        else:
            query = "DELETE FROM messages;"
            params = ()
        await self.db.execute(query, params)
