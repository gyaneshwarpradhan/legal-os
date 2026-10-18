"""OpenAI provider implementation."""
import os
import time
from typing import List

from app.ai.providers.base import LLMMessage, LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o",
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model

    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        import httpx

        start_time = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        formatted_messages = [
            {"role": m.role, "content": m.content} for m in messages
        ]

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()

        latency_ms = int((time.time() - start_time) * 1000)
        content_text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        return LLMResponse(
            content=content_text,
            model=self.model,
            token_count_input=usage.get("prompt_tokens", 0),
            token_count_output=usage.get("completion_tokens", 0),
            latency_ms=latency_ms,
            raw_response=data,
        )
