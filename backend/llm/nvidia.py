import json
import time
from typing import Any, AsyncIterator, Dict, List, Optional
import httpx
from backend.config.settings import settings
from backend.utils.logger import logger
from backend.llm.base import LLMProvider, LLMResponse, LLMToolCall, ProviderHealth


class NVIDIAProvider(LLMProvider):
    """Primary Cloud AI Provider using the NVIDIA API (build.nvidia.com / integrate.api.nvidia.com)."""

    provider_name: str = "nvidia"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self._api_key = api_key or settings.nvidia.api_key.get_secret_value()
        self.base_url = (base_url or settings.nvidia.base_url).rstrip("/")
        self.model = model or settings.nvidia.model

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    def _get_headers(self) -> Dict[str, str]:
        if not self.is_configured:
            raise ValueError(
                "NVIDIA API Key is missing. Please configure NVIDIA_API_KEY in your .env file."
            )
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

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

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=self._get_headers(), json=payload)
                response.raise_for_status()
                data = response.json()
                choice = data["choices"][0]
                message = choice["message"]

                tool_calls: List[LLMToolCall] = []
                if "tool_calls" in message and message["tool_calls"]:
                    for tc in message["tool_calls"]:
                        fn = tc.get("function", {})
                        args = fn.get("arguments", "{}")
                        try:
                            parsed_args = json.loads(args) if isinstance(args, str) else args
                        except Exception:
                            parsed_args = {"raw": args}
                        tool_calls.append(
                            LLMToolCall(
                                id=tc.get("id", ""),
                                name=fn.get("name", ""),
                                arguments=parsed_args,
                            )
                        )

                return LLMResponse(
                    content=message.get("content") or "",
                    tool_calls=tool_calls,
                    provider=self.provider_name,
                    model=payload["model"],
                    finish_reason=choice.get("finish_reason"),
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"NVIDIA API HTTP error: {e.response.status_code} - {e.response.text}")
                raise RuntimeError(f"NVIDIA API error: {e.response.status_code} - {e.response.text}") from e
            except Exception as e:
                logger.error(f"NVIDIA API request failed: {e}")
                raise RuntimeError(f"NVIDIA connection failed: {e}") from e

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

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                async with client.stream(
                    "POST", url, headers=self._get_headers(), json=payload
                ) as response:
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
            except httpx.HTTPStatusError as e:
                logger.error(f"NVIDIA API streaming error: {e.response.status_code}")
                raise RuntimeError(f"NVIDIA API streaming error: {e.response.status_code}") from e
            except Exception as e:
                logger.error(f"NVIDIA streaming failed: {e}")
                raise RuntimeError(f"NVIDIA stream failed: {e}") from e

    async def generate_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(url, headers=self._get_headers(), json=payload)
                response.raise_for_status()
                data = response.json()
                choice = data["choices"][0]
                message = choice["message"]

                tool_calls: List[LLMToolCall] = []
                if "tool_calls" in message and message["tool_calls"]:
                    for tc in message["tool_calls"]:
                        fn = tc.get("function", {})
                        args = fn.get("arguments", "{}")
                        try:
                            parsed_args = json.loads(args) if isinstance(args, str) else args
                        except Exception:
                            parsed_args = {"raw": args}
                        tool_calls.append(
                            LLMToolCall(
                                id=tc.get("id", ""),
                                name=fn.get("name", ""),
                                arguments=parsed_args,
                            )
                        )

                return LLMResponse(
                    content=message.get("content") or "",
                    tool_calls=tool_calls,
                    provider=self.provider_name,
                    model=payload["model"],
                    finish_reason=choice.get("finish_reason"),
                )
            except Exception as e:
                logger.error(f"NVIDIA tool call failed: {e}")
                raise RuntimeError(f"NVIDIA tool call failed: {e}") from e

    async def health_check(self) -> ProviderHealth:
        if not self.is_configured:
            return ProviderHealth(
                provider=self.provider_name,
                status="not_configured",
                model=self.model,
                error="NVIDIA_API_KEY is not set in environment.",
            )

        start_time = time.time()
        url = f"{self.base_url}/models"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers=self._get_headers())
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
                        error=f"HTTP {res.status_code}: {res.text[:100]}",
                    )
        except Exception as e:
            latency = round((time.time() - start_time) * 1000, 1)
            return ProviderHealth(
                provider=self.provider_name,
                status="unavailable",
                model=self.model,
                latency_ms=latency,
                error=str(e),
            )
