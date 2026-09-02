import json
import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport, Response
from backend.api.app import app
from backend.database.manager import db
from backend.llm.base import LLMResponse, LLMToolCall, ProviderHealth
from backend.llm.nvidia import NVIDIAProvider
from backend.llm.local import LocalProvider
from backend.llm.manager import LLMManager
from backend.config.settings import settings


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_llm_api.db"
    monkeypatch.setattr(db, "db_path", test_db_path)
    db.initialize_db()


def test_nvidia_provider_unconfigured():
    """Verify NVIDIA provider correctly detects unconfigured API key."""
    provider = NVIDIAProvider(api_key="")
    assert not provider.is_configured
    with pytest.raises(ValueError, match="NVIDIA API Key is missing"):
        provider._get_headers()


@pytest.mark.asyncio
async def test_nvidia_provider_health_unconfigured():
    """Verify health check returns not_configured status without key."""
    provider = NVIDIAProvider(api_key="")
    health = await provider.health_check()
    assert health.status == "not_configured"
    assert "NVIDIA_API_KEY is not set" in (health.error or "")


@pytest.mark.asyncio
async def test_nvidia_provider_generate_mock():
    """Verify NVIDIA provider generation using mocked httpx response."""
    provider = NVIDIAProvider(api_key="nvapi-test-key", model="meta/llama-3.3-70b-instruct")

    mock_response_data = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Opening VS Code.",
                },
                "finish_reason": "stop",
            }
        ]
    }

    mock_request = httpx.Request("POST", "https://integrate.api.nvidia.com/v1/chat/completions")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Response(200, json=mock_response_data, request=mock_request)
        res = await provider.generate([{"role": "user", "content": "Open VS Code."}])
        assert isinstance(res, LLMResponse)
        assert res.content == "Opening VS Code."
        assert res.provider == "nvidia"
        assert res.model == "meta/llama-3.3-70b-instruct"


@pytest.mark.asyncio
async def test_nvidia_provider_tool_calls_mock():
    """Verify NVIDIA provider handles structured tool calls."""
    provider = NVIDIAProvider(api_key="nvapi-test-key")

    mock_response_data = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "type": "function",
                            "function": {
                                "name": "filesystem_list_dir",
                                "arguments": json.dumps({"path": "."}),
                            },
                        }
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ]
    }

    mock_request = httpx.Request("POST", "https://integrate.api.nvidia.com/v1/chat/completions")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = Response(200, json=mock_response_data, request=mock_request)
        res = await provider.generate_with_tools(
            [{"role": "user", "content": "list directory"}],
            tools=[{"type": "function", "function": {"name": "filesystem_list_dir"}}]
        )
        assert len(res.tool_calls) == 1
        assert res.tool_calls[0].name == "filesystem_list_dir"
        assert res.tool_calls[0].arguments == {"path": "."}


@pytest.mark.asyncio
async def test_llm_manager_fallback():
    """Verify LLMManager falls back to local provider when primary fails and fallback is enabled."""
    manager = LLMManager()

    # Create mock failing primary
    mock_nvidia = AsyncMock()
    mock_nvidia.generate.side_effect = RuntimeError("NVIDIA API 503 Outage")
    manager.register_provider("nvidia", mock_nvidia)

    # Create mock working fallback
    mock_local = AsyncMock()
    mock_local.generate.return_value = LLMResponse(
        content="Fallback response from local model",
        provider="local",
        model="llama3.2:3b"
    )
    manager.register_provider("local", mock_local)

    res = await manager.generate([{"role": "user", "content": "Hello"}], provider_name="nvidia")
    assert res.content == "Fallback response from local model"
    assert res.provider == "local"


@pytest.mark.asyncio
async def test_api_llm_status():
    """Verify /api/llm/status returns provider states without exposing secrets."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/llm/status")
        assert res.status_code == 200
        data = res.json()
        assert "active_provider" in data
        assert "providers" in data
        assert "nvidia" in data["providers"]
        assert "local" in data["providers"]
        assert data["providers"]["nvidia"]["model"] is not None
        # Verify secret key is never leaked
        assert "api_key" not in data["providers"]["nvidia"]


@pytest.mark.asyncio
async def test_api_llm_select_provider():
    """Verify runtime provider selection endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/llm/select-provider", json={
            "provider": "local",
            "execution_mode": "local"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["active_provider"] == "local"
        assert data["execution_mode"] == "local"

        # Switch back to nvidia
        res2 = await client.post("/api/llm/select-provider", json={
            "provider": "nvidia",
            "execution_mode": "cloud"
        })
        assert res2.status_code == 200
        assert res2.json()["active_provider"] == "nvidia"


@pytest.mark.asyncio
async def test_chat_stream_endpoint():
    """Verify /api/chat/stream SSE endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create conversation
        conv_res = await client.post("/api/conversations", json={"title": "Stream Test"})
        conv_id = conv_res.json()["id"]

        # Mock LLMManager stream
        async def mock_stream(*args, **kwargs):
            yield "Hello "
            yield "from "
            yield "JARVIS!"

        with patch("backend.llm.manager.llm_manager.stream", side_effect=mock_stream):
            stream_res = await client.post("/api/chat/stream", json={
                "conversation_id": conv_id,
                "content": "Hi there"
            })
            assert stream_res.status_code == 200
            assert "text/event-stream" in stream_res.headers["content-type"]
            body = stream_res.text
            assert "Hello " in body
            assert "from " in body
            assert "JARVIS!" in body
            assert "[DONE]" in body

        # Verify messages persisted
        detail_res = await client.get(f"/api/conversations/{conv_id}")
        assert detail_res.status_code == 200
        msgs = detail_res.json()["messages"]
        assert len(msgs) == 2
        assert msgs[0]["role"] == "user"
        assert msgs[1]["role"] == "assistant"
        assert msgs[1]["content"] == "Hello from JARVIS!"
