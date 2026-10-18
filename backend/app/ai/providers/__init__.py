"""LLM provider factory and registry."""
import os
from typing import Optional

from app.ai.providers.anthropic import AnthropicProvider
from app.ai.providers.base import LLMMessage, LLMProvider, LLMResponse
from app.ai.providers.mock import LocalMockLLMProvider
from app.ai.providers.openai import OpenAIProvider


def get_llm_provider(provider_name: Optional[str] = None) -> LLMProvider:
    """
    Return configured LLM provider.
    Priority:
    1. Explicit provider_name if passed
    2. Anthropic (if ANTHROPIC_API_KEY set)
    3. OpenAI (if OPENAI_API_KEY set)
    4. LocalMockLLMProvider (default for testing/local dev)
    """
    if provider_name == "anthropic":
        return AnthropicProvider()
    elif provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "mock":
        return LocalMockLLMProvider()

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key and anthropic_key.strip():
        return AnthropicProvider(api_key=anthropic_key)

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.strip():
        return OpenAIProvider(api_key=openai_key)

    return LocalMockLLMProvider()
