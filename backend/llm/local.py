import json
import time
from typing import Any, AsyncIterator, Dict, List, Optional
import httpx
from backend.config.settings import settings
from backend.utils.logger import logger
from backend.llm.base import LLMProvider, LLMResponse, LLMToolCall, ProviderHealth


class LocalProvider(LLMProvider):
    """Local LLM Provider running quantized models on local hardware (Ollama / vLLM)."""

    provider_name: str = "local"

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        runtime: Optional[str] = None,
    ):
        self.base_url = (base_url or settings.local_llm.url).rstrip("/")
        self.model = model or settings.local_llm.model
        self.runtime = runtime or settings.local_llm.runtime

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                choice = data["choices"][0]
                message = choice["message"]

                return LLMResponse(
                    content=message.get("content") or "",
                    tool_calls=[],
                    provider=self.provider_name,
                    model=payload["model"],
                    finish_reason=choice.get("finish_reason"),
                )
            except Exception as e:
                logger.error(f"Local LLM generation failed: {e}")
                raise RuntimeError(f"Local LLM ({self.runtime}) unavailable: {e}") from e

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncIterator[str]:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        line = line.strip()
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            choice = chunk["choices"][0]
                            delta = choice.get("delta", {})
                            content = delta.get("content")
                            if content:
                                yield content
                        except Exception:
                            continue
            except Exception as e:
                logger.error(f"Local LLM streaming failed: {e}")
                raise RuntimeError(f"Local LLM ({self.runtime}) stream failed: {e}") from e

    async def generate_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        # Fallback to standard generation if local model does not support native tools
        return await self.generate(messages, temperature=temperature, max_tokens=max_tokens, **kwargs)

    async def health_check(self) -> ProviderHealth:
        start_time = time.time()
        url = f"{self.base_url}/models"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url)
                latency = round((time.time() - start_time) * 1000, 1)
                if res.status_code == 200:
                    return ProviderHealth(
                        provider=self.provider_name,
                        status="connected",
                        model=self.model,
                        latency_ms=latency,
                    )
                else:
                    return ProviderHealth(
                        provider=self.provider_name,
                        status="unavailable",
                        model=self.model,
                        latency_ms=latency,
                        error=f"Local runtime returned HTTP {res.status_code}",
                    )
        except Exception as e:
            latency = round((time.time() - start_time) * 1000, 1)
            return ProviderHealth(
                provider=self.provider_name,
                status="unavailable",
                model=self.model,
                latency_ms=latency,
                error=f"{self.runtime} service not responding at {self.base_url}",
            )
