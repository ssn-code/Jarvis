import pytest
from datetime import datetime, timezone
from app.models.domain import AgentMessage, MessageRole
from app.services.database import DatabaseManager
from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory


@pytest.fixture
def temp_db_mgr(tmp_path):
    """Fixture that provides an isolated SQLite database manager."""
    db_file = tmp_path / "test_memory.db"
    db_mgr = DatabaseManager(db_path=db_file)
    db_mgr.initialize_db()
    return db_mgr


@pytest.fixture
def temp_chroma_dir(tmp_path):
    """Fixture that provides an isolated directory path for ChromaDB."""
    return tmp_path / "chroma"


@pytest.mark.asyncio
async def test_short_term_memory(temp_db_mgr):
    """Test short-term memory message additions, retrieval order, limits, and clearing."""
    stm = ShortTermMemory(db_manager=temp_db_mgr)
    
    # Verify starting state is empty
    history = await stm.get_history()
    assert len(history) == 0
    
    # Insert messages
    msg1 = AgentMessage(role=MessageRole.USER, content="Hello JARVIS")
    msg2 = AgentMessage(role=MessageRole.ASSISTANT, content="Hello! How can I help you today?")
    msg3 = AgentMessage(role=MessageRole.USER, content="Run a system report")
    
    await stm.add_message(msg1, task_id="task-x")
    await stm.add_message(msg2, task_id="task-x")
    await stm.add_message(msg3)  # global message without task association
    
    # Verify task-specific history (chronological order)
    task_history = await stm.get_history(task_id="task-x")
    assert len(task_history) == 2
    assert task_history[0].content == "Hello JARVIS"
    assert task_history[1].content == "Hello! How can I help you today?"
    
    # Verify global history (contains everything)
    global_history = await stm.get_history()
    assert len(global_history) == 3
    assert global_history[2].content == "Run a system report"
    
    # Test limit filter
    limited_history = await stm.get_history(limit=2)
    assert len(limited_history) == 2
    # Capped at most recent 2, ordered chronologically
    assert limited_history[0].content == "Hello! How can I help you today?"
    assert limited_history[1].content == "Run a system report"
    
    # Clear history
    await stm.clear_history(task_id="task-x")
    cleared_task_hist = await stm.get_history(task_id="task-x")
    assert len(cleared_task_hist) == 0
    
    # Global messages should still remain
    remaining = await stm.get_history()
    assert len(remaining) == 1
    assert remaining[0].content == "Run a system report"


@pytest.mark.asyncio
async def test_long_term_memory(temp_chroma_dir):
    """Test vector storage, searches, filters, deletions, and clear operations inside ChromaDB."""
    ltm = LongTermMemory(chroma_dir=temp_chroma_dir)
    ltm.initialize()
    
    # Store some preferences and context
    id1 = await ltm.add_memory(
        text="I always use VS Code for programming python.",
        category="preferences",
        metadata={"priority": "high"}
    )
    id2 = await ltm.add_memory(
        text="I prefer using Google Chrome for web research.",
        category="preferences"
    )
    id3 = await ltm.add_memory(
        text="I work on the CyberX repository under d:/projects/CyberX.",
        category="workspaces"
    )
    
    # Verify dynamic IDs are generated
    assert isinstance(id1, str) and len(id1) > 0
    assert isinstance(id3, str) and len(id3) > 0
    
    # Query without category filter
    results = await ltm.search_memories(query="Which IDE do I write Python in?", limit=1)
    assert len(results) == 1
    assert "VS Code" in results[0]["text"]
    assert results[0]["metadata"]["category"] == "preferences"
    assert results[0]["metadata"]["priority"] == "high"
    
    # Query with category filter (should not match workspace even if similar)
    results_pref = await ltm.search_memories(
        query="projects and workspaces directory paths", 
        category="preferences", 
        limit=5
    )
    for res in results_pref:
        assert res["metadata"]["category"] == "preferences"
        assert "CyberX" not in res["text"]
        
    # Verify finding workspace memories
    results_ws = await ltm.search_memories(
        query="workspace and project paths", 
        category="workspaces", 
        limit=1
    )
    assert len(results_ws) == 1
    assert "CyberX" in results_ws[0]["text"]
    
    # Delete memory
    await ltm.delete_memory(id1)
    results_after_delete = await ltm.search_memories(query="Which IDE do I write Python in?", limit=1)
    # The chrome memory might match now, or nothing relevant, but it should not match VS Code
    if results_after_delete:
        assert "VS Code" not in results_after_delete[0]["text"]
        
    # Clear all memories
    await ltm.clear_all()
    results_cleared = await ltm.search_memories(query="Chrome browser preferences", limit=5)
    assert len(results_cleared) == 0
