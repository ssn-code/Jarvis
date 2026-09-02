import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models import (
    PermissionLevel,
    ToolMetadata,
    TaskStep,
    StepStatus,
    TaskPlan,
    PlanStatus,
    AgentMessage,
    MessageRole,
)


def test_tool_metadata_validation():
    """Verify tool metadata model validation and defaults."""
    tool = ToolMetadata(
        name="open_browser",
        description="Opens a browser tab",
        input_schema={"type": "object", "properties": {"url": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"success": {"type": "boolean"}}},
    )
    
    assert tool.name == "open_browser"
    assert tool.permission_level == PermissionLevel.SAFE
    
    # Verify missing fields raises validation error
    with pytest.raises(ValidationError):
        ToolMetadata(name="incomplete_tool")


def test_task_plan_structure():
    """Verify task plan decomposition model and step status changes."""
    step = TaskStep(
        step_id=1,
        description="Launch Chrome",
        tool_name="open_browser",
        tool_input={"url": "https://google.com"},
    )
    
    assert step.status == StepStatus.PENDING
    
    plan = TaskPlan(
        task_id="plan-uuid-123",
        prompt="Open google in browser",
        steps=[step],
    )
    
    assert plan.status == PlanStatus.PENDING
    assert len(plan.steps) == 1
    assert plan.steps[0].step_id == 1


def test_agent_message():
    """Verify agent message fields and role checks."""
    msg = AgentMessage(
        role=MessageRole.USER,
        content="Hello JARVIS!",
        metadata={"user_id": 42}
    )
    
    assert msg.role == MessageRole.USER
    assert msg.content == "Hello JARVIS!"
    assert msg.metadata["user_id"] == 42
    assert isinstance(msg.timestamp, datetime)
