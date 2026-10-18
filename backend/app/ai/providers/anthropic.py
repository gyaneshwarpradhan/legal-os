"""Anthropic Claude provider implementation."""
import os
import time
from typing import List

from app.ai.providers.base import LLMMessage, LLMProvider, LLMResponse


class AnthropicProvider(LLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-3-5-sonnet-20241022",
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model

    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        import httpx

        start_time = time.time()

        system_prompt = ""
        user_assistant_messages = []
        for m in messages:
            if m.role == "system":
                system_prompt = m.content
            else:
                user_assistant_messages.append({"role": m.role, "content": m.content})

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        payload = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": user_assistant_messages,
        }
        if system_prompt:
            payload["system"] = system_prompt

        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()

        latency_ms = int((time.time() - start_time) * 1000)
        content_text = "".join(
            block["text"] for block in data.get("content", []) if block.get("type") == "text"
        )
        usage = data.get("usage", {})

        return LLMResponse(
            content=content_text,
            model=self.model,
            token_count_input=usage.get("input_tokens", 0),
            token_count_output=usage.get("output_tokens", 0),
            latency_ms=latency_ms,
            raw_response=data,
        )
