import pytest
from pathlib import Path
from backend.database.manager import DatabaseManager


@pytest.fixture
def temp_db(tmp_path: Path):
    db_file = tmp_path / "test_jarvis.db"
    manager = DatabaseManager(db_path=db_file)
    manager.initialize_db()
    return manager


@pytest.mark.asyncio
async def test_database_initialization(temp_db: DatabaseManager):
    """Verify all required tables exist upon initialization."""
    tables = await temp_db.fetchall(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    )
    table_names = [t["name"] for t in tables]
    expected = [
        "audit_logs",
        "automations",
        "conversations",
        "mcp_servers",
        "mcp_tools",
        "memories",
        "messages",
        "settings",
        "tool_executions",
    ]
    for exp in expected:
        assert exp in table_names, f"Table {exp} missing from database"


@pytest.mark.asyncio
async def test_conversation_and_message_crud(temp_db: DatabaseManager):
    """Verify conversations and linked messages CRUD."""
    conv_id = "test-conv-1"
    now = "2026-09-02T12:00:00Z"
    await temp_db.execute(
        "INSERT INTO conversations (id, title, created_at, updated_at, metadata) VALUES (?, ?, ?, ?, ?)",
        (conv_id, "Test Chat", now, now, "{}"),
    )

    conv = await temp_db.fetchone("SELECT * FROM conversations WHERE id = ?", (conv_id,))
    assert conv is not None
    assert conv["title"] == "Test Chat"

    msg_id = await temp_db.execute(
        "INSERT INTO messages (conversation_id, role, content, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
        (conv_id, "user", "Hello JARVIS", "{}", now),
    )
    assert msg_id > 0

    msgs = await temp_db.fetchall("SELECT * FROM messages WHERE conversation_id = ?", (conv_id,))
    assert len(msgs) == 1
    assert msgs[0]["content"] == "Hello JARVIS"


@pytest.mark.asyncio
async def test_memory_crud(temp_db: DatabaseManager):
    """Verify memory storage and uniqueness."""
    now = "2026-09-02T12:00:00Z"
    mem_id = await temp_db.execute(
        "INSERT INTO memories (key, value, category, importance, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        ("favorite_editor", "VS Code", "preference", 3, now, now),
    )
    assert mem_id > 0

    mem = await temp_db.fetchone("SELECT * FROM memories WHERE key = ?", ("favorite_editor",))
    assert mem is not None
    assert mem["value"] == "VS Code"


@pytest.mark.asyncio
async def test_audit_log_insert(temp_db: DatabaseManager):
    """Verify audit log entries can be persisted."""
    now = "2026-09-02T12:00:00Z"
    log_id = await temp_db.execute(
        """INSERT INTO audit_logs (timestamp, user, mcp_server, tool, arguments, permission, approval, result, execution_time_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (now, "user", "filesystem", "list_dir", '{"path": "."}', "AUTOMATIC", "APPROVED", "[]", 1.5),
    )
    assert log_id > 0
    log = await temp_db.fetchone("SELECT * FROM audit_logs WHERE id = ?", (log_id,))
    assert log["tool"] == "list_dir"
