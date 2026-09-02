from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional
from pydantic import BaseModel, Field


class LLMToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    content: str = ""
    tool_calls: List[LLMToolCall] = Field(default_factory=list)
    provider: str
    model: str
    finish_reason: Optional[str] = None


class ProviderHealth(BaseModel):
    provider: str
    status: str  # "connected" | "unavailable" | "not_configured"
    model: str
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class LLMProvider(ABC):
    """Abstract Base Class for all JARVIS LLM Providers (NVIDIA, Local, OpenRouter, Gemini)."""

    provider_name: str = "base"

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """Generate a complete response from the LLM."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response tokens progressively."""
        pass

    @abstractmethod
    async def generate_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """Generate a response with structured MCP/function tools."""
        pass

    def count_tokens(self, text: str) -> int:
        """Heuristic token estimator (approx 4 chars per token). Can be overridden."""
        return max(1, len(text) // 4)

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Perform a non-intrusive connectivity and authorization check."""
        pass
