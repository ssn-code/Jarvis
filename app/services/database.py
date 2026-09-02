import sqlite3
import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.config import settings
from app.utils.logger import logger


class DatabaseManager:
    """Manages the lifecycle, schema, and queries of the local SQLite database in an async-safe manner."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.db.sqlite_db_path
        self._lock = asyncio.Lock()

    def _get_connection(self) -> sqlite3.Connection:
        """Creates a synchronous connection, setting WAL mode, FK constraints, and Row factories."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable structural constraints and modern concurrency
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def initialize_db(self) -> None:
        """Create tables in the database if they do not exist. Call on startup."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = self._get_connection()
        try:
            with conn:
                # 1. Tasks Table (Planner plans)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        task_id TEXT PRIMARY KEY,
                        prompt TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        completed_at TEXT
                    );
                """)
                
                # 2. Task Steps Table (Planner steps breakdown)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS task_steps (
                        task_id TEXT NOT NULL,
                        step_id INTEGER NOT NULL,
                        description TEXT NOT NULL,
                        tool_name TEXT,
                        tool_input TEXT,
                        status TEXT NOT NULL,
                        result TEXT,
                        error TEXT,
                        PRIMARY KEY (task_id, step_id),
                        FOREIGN KEY (task_id) REFERENCES tasks (task_id) ON DELETE CASCADE
                    );
                """)
                
                # 3. Messages Table (Short-term Conversation History)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_id TEXT,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        metadata TEXT NOT NULL
                    );
                """)
            logger.info(f"SQLite database initialized successfully at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite database: {e}")
            raise e
        finally:
            conn.close()

    async def execute(self, query: str, params: tuple = ()) -> None:
        """Asynchronously executes a write query (INSERT, UPDATE, DELETE)."""
        async with self._lock:
            await asyncio.to_thread(self._execute_sync, query, params)

    def _execute_sync(self, query: str, params: tuple) -> None:
        conn = self._get_connection()
        try:
            with conn:
                conn.execute(query, params)
        except Exception as e:
            logger.error(f"Database write execution failed: {e}. Query: {query}")
            raise e
        finally:
            conn.close()

    async def fetchall(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Asynchronously executes a read query and returns all matching rows as dicts."""
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
            logger.error(f"Database fetchall execution failed: {e}. Query: {query}")
            raise e
        finally:
            conn.close()

    async def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Asynchronously executes a read query and returns the first matching row as a dict."""
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
            logger.error(f"Database fetchone execution failed: {e}. Query: {query}")
            raise e
        finally:
            conn.close()


# Shared instance
db = DatabaseManager()
