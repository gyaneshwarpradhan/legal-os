"""Abstract base classes and schemas for LLM provider abstraction."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LLMMessage:
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    content: str
    model: str
    token_count_input: int
    token_count_output: int
    latency_ms: int
    raw_response: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate a response given a conversation history."""
        pass
