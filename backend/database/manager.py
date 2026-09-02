import sqlite3
import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from backend.config.settings import settings
from backend.utils.logger import logger


def utc_iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DatabaseManager:
    """Async-safe SQLite database manager for JARVIS."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.db.sqlite_db_path
        self._lock = asyncio.Lock()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def initialize_db(self) -> None:
        """Create database tables if they do not exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._get_connection()
        try:
            with conn:
                # 1. Conversations
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        metadata TEXT NOT NULL DEFAULT '{}'
                    );
                """)

                # 2. Messages
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        tool_calls TEXT,
                        metadata TEXT NOT NULL DEFAULT '{}',
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
                    );
                """)

                # 3. Memories
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT NOT NULL UNIQUE,
                        value TEXT NOT NULL,
                        category TEXT NOT NULL DEFAULT 'preference',
                        importance INTEGER DEFAULT 1,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                """)

                # 4. MCP Servers
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS mcp_servers (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT DEFAULT '',
                        command TEXT DEFAULT '',
                        args TEXT DEFAULT '[]',
                        transport TEXT DEFAULT 'stdio',
                        status TEXT DEFAULT 'disconnected',
                        enabled INTEGER DEFAULT 1,
                        auto_activation INTEGER DEFAULT 1,
                        permission_level TEXT DEFAULT 'AUTOMATIC'
                    );
                """)

                # 5. MCP Tools
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS mcp_tools (
                        id TEXT PRIMARY KEY,
                        server_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT DEFAULT '',
                        input_schema TEXT DEFAULT '{}',
                        output_schema TEXT DEFAULT '{}',
                        risk_level TEXT DEFAULT 'SAFE',
                        FOREIGN KEY (server_id) REFERENCES mcp_servers (id) ON DELETE CASCADE
                    );
                """)

                # 6. Tool Executions
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tool_executions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tool_name TEXT NOT NULL,
                        server_id TEXT,
                        arguments TEXT DEFAULT '{}',
                        result TEXT,
                        status TEXT DEFAULT 'success',
                        execution_time_ms REAL DEFAULT 0,
                        created_at TEXT NOT NULL
                    );
                """)

                # 7. Automations
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS automations (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        trigger_type TEXT NOT NULL,
                        schedule_cron TEXT,
                        action_payload TEXT DEFAULT '{}',
                        enabled INTEGER DEFAULT 1,
                        last_run TEXT,
                        created_at TEXT NOT NULL
                    );
                """)

                # 8. Settings Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                """)

                # 9. Audit Logs
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user TEXT NOT NULL DEFAULT 'user',
                        mcp_server TEXT,
                        tool TEXT,
                        arguments TEXT,
                        permission TEXT NOT NULL DEFAULT 'AUTOMATIC',
                        approval TEXT NOT NULL DEFAULT 'APPROVED',
                        result TEXT,
                        execution_time_ms REAL DEFAULT 0,
                        error TEXT
                    );
                """)

            logger.info(f"Database initialized successfully at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise e
        finally:
            conn.close()

    async def execute(self, query: str, params: tuple = ()) -> int:
        """Asynchronously executes an INSERT, UPDATE, or DELETE query and returns lastrowid."""
        async with self._lock:
            return await asyncio.to_thread(self._execute_sync, query, params)

    def _execute_sync(self, query: str, params: tuple) -> int:
        conn = self._get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.lastrowid or cursor.rowcount
        except Exception as e:
            logger.error(f"DB execute failed: {e}. Query: {query}")
            raise e
        finally:
            conn.close()

    async def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Asynchronously executes a read query and returns all rows as dicts."""
        async with self._lock:
            return await asyncio.to_thread(self._fetchall_sync, query, params)

    def _fetchall_sync(self, query: str, params: tuple) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"DB fetchall failed: {e}. Query: {query}")
            raise e
        finally:
            conn.close()

    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Asynchronously executes a read query and returns the first matching row."""
        async with self._lock:
            return await asyncio.to_thread(self._fetchone_sync, query, params)

    def _fetchone_sync(self, query: str, params: tuple) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"DB fetchone failed: {e}. Query: {query}")
            raise e
        finally:
            conn.close()


# Shared singleton instance
db = DatabaseManager()
