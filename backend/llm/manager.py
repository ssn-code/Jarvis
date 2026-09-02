from typing import Any, AsyncIterator, Dict, List, Optional
from backend.config.settings import settings
from backend.utils.logger import logger
from backend.llm.base import LLMProvider, LLMResponse, ProviderHealth
from backend.llm.nvidia import NVIDIAProvider
from backend.llm.local import LocalProvider


class LLMManager:
    """Manages AI providers, model routing, streaming, and graceful fallbacks."""

    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {
            "nvidia": NVIDIAProvider(),
            "local": LocalProvider(),
        }

    def register_provider(self, name: str, provider: LLMProvider):
        """Register or override an LLM provider."""
        self._providers[name] = provider

    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        """Retrieve a specific provider or the default primary provider."""
        target = name or settings.llm.provider
        if target not in self._providers:
            raise ValueError(f"Unknown LLM provider: {target}. Available: {list(self._providers.keys())}")
        return self._providers[target]

    async def generate(
        self,
        messages: List[Dict[str, Any]],
        provider_name: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response with primary provider and optional fallback."""
        primary_name = provider_name or settings.llm.provider
        primary = self.get_provider(primary_name)

        try:
            return await primary.generate(messages, **kwargs)
        except Exception as primary_error:
            logger.warning(f"Primary provider '{primary_name}' failed: {primary_error}")

            if settings.llm.enable_fallback:
                fallback_name = "local" if primary_name == "nvidia" else "nvidia"
                fallback = self._providers.get(fallback_name)
                if fallback:
                    logger.info(f"Attempting fallback to '{fallback_name}' provider...")
                    try:
                        return await fallback.generate(messages, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Fallback provider '{fallback_name}' also failed: {fallback_error}")

            # If no provider succeeded:
            raise RuntimeError(
                f"No AI provider is currently available. {primary_error}. Check your model configuration."
            ) from primary_error

    async def stream(
        self,
        messages: List[Dict[str, Any]],
        provider_name: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response with primary provider and optional fallback."""
        primary_name = provider_name or settings.llm.provider
        primary = self.get_provider(primary_name)

        fallback_needed = False
        primary_error_msg = ""

        try:
            async for token in primary.stream(messages, **kwargs):
                yield token
            return
        except Exception as e:
            primary_error_msg = str(e)
            logger.warning(f"Primary streaming with '{primary_name}' failed: {e}")
            fallback_needed = settings.llm.enable_fallback

        if fallback_needed:
            fallback_name = "local" if primary_name == "nvidia" else "nvidia"
            fallback = self._providers.get(fallback_name)
            if fallback:
                logger.info(f"Streaming fallback switching to '{fallback_name}'...")
                yield f"\n\n*[Notice: Primary provider ({primary_name}) unavailable. Switching to {fallback_name} model...]*\n\n"
                try:
                    async for token in fallback.stream(messages, **kwargs):
                        yield token
                    return
                except Exception as fb_err:
                    logger.error(f"Fallback stream failed: {fb_err}")
                    yield f"\n\n[Error: Fallback model also unavailable: {fb_err}]"
                    return

        raise RuntimeError(f"NVIDIA API unavailable: {primary_error_msg}")

    async def health_check_all(self) -> Dict[str, ProviderHealth]:
        """Run health checks across all registered providers."""
        results = {}
        for name, provider in self._providers.items():
            results[name] = await provider.health_check()
        return results

    async def health_check_provider(self, name: str) -> ProviderHealth:
        """Run health check for a single provider."""
        return await self.get_provider(name).health_check()


# Shared singleton instance
llm_manager = LLMManager()
