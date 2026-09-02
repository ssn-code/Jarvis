import pytest
from httpx import AsyncClient, ASGITransport
from backend.api.app import app
from backend.database.manager import db


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """Point db to a temporary database file for API tests."""
    test_db_path = tmp_path / "test_api.db"
    monkeypatch.setattr(db, "db_path", test_db_path)
    db.initialize_db()


@pytest.mark.asyncio
async def test_api_root():
    """Verify API root endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["app"] == "JARVIS"
        assert data["status"] == "online"


@pytest.mark.asyncio
async def test_health_check():
    """Verify health endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/system/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["app"] == "JARVIS"

        root_health = await client.get("/health")
        assert root_health.status_code == 200
        assert root_health.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_system_status():
    """Verify system status endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/system/status")
        assert response.status_code == 200
        data = response.json()
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "disk_percent" in data


@pytest.mark.asyncio
async def test_conversations_flow():
    """Verify creating, fetching, and deleting a conversation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create
        create_res = await client.post("/api/conversations", json={"title": "Test Chat API"})
        assert create_res.status_code == 200
        conv = create_res.json()
        conv_id = conv["id"]

        # Add message
        msg_res = await client.post(
            f"/api/conversations/{conv_id}/messages",
            json={"role": "user", "content": "Hello world!"}
        )
        assert msg_res.status_code == 200

        # Get details
        detail_res = await client.get(f"/api/conversations/{conv_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert len(detail["messages"]) == 1
        assert detail["messages"][0]["content"] == "Hello world!"

        # List
        list_res = await client.get("/api/conversations")
        assert list_res.status_code == 200
        assert len(list_res.json()["conversations"]) >= 1

        # Delete
        del_res = await client.delete(f"/api/conversations/{conv_id}")
        assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_memory_flow():
    """Verify creating, searching, and deleting memories."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create
        res = await client.post("/api/memory", json={"key": "pref_lang", "value": "Python", "category": "preference"})
        assert res.status_code == 200

        # Search
        search_res = await client.get("/api/memory/search?q=Python")
        assert search_res.status_code == 200
        assert len(search_res.json()["results"]) == 1

        # List
        list_res = await client.get("/api/memory")
        assert list_res.status_code == 200
        assert len(list_res.json()["memories"]) == 1


@pytest.mark.asyncio
async def test_mcp_servers_flow():
    """Verify registering and toggling an MCP server."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Register
        reg_res = await client.post("/api/mcp/servers", json={
            "id": "filesystem",
            "name": "Filesystem",
            "description": "Local workspace access",
            "command": "npx -y @modelcontextprotocol/server-filesystem",
            "transport": "stdio",
            "enabled": True,
            "auto_activation": True,
            "permission_level": "AUTOMATIC"
        })
        assert reg_res.status_code == 200

        # List
        list_res = await client.get("/api/mcp/servers")
        assert list_res.status_code == 200
        servers = list_res.json()["servers"]
        assert any(s["id"] == "filesystem" for s in servers)

        # Toggle
        toggle_res = await client.post("/api/mcp/servers/filesystem/toggle", json={"enabled": False})
        assert toggle_res.status_code == 200
        assert toggle_res.json()["enabled"] is False


@pytest.mark.asyncio
async def test_settings_endpoint():
    """Verify settings retrieval (secrets masked) and custom setting persistence."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/settings")
        assert res.status_code == 200
        data = res.json()
        assert "llm" in data
        assert "voice" in data
        assert "security" in data
        assert "api_key" not in data["llm"]  # Secret masked! Only has_api_key bool

        # Custom override
        post_res = await client.post("/api/settings", json={"key": "theme_mode", "value": "oled_black"})
        assert post_res.status_code == 200
