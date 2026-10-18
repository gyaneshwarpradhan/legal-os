"""Grounded local mock LLM provider for zero-dependency offline development and testing."""
import re
import time
from typing import List

from app.ai.providers.base import LLMMessage, LLMProvider, LLMResponse


class LocalMockLLMProvider(LLMProvider):
    def __init__(self, model: str = "mock-claude-3-5-sonnet"):
        self.model = model

    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        start_time = time.time()

        user_content = ""
        system_content = ""
        for m in messages:
            if m.role == "system":
                system_content = m.content
            elif m.role == "user":
                user_content = m.content

        # Check if context was provided in the prompt
        context_blocks = re.findall(
            r"\[DOCUMENT_CHUNK_ID:\s*([a-f0-9\-]+)\](.*?)\[/DOCUMENT_CHUNK_ID\]",
            user_content,
            re.DOTALL | re.IGNORECASE,
        )

        if not context_blocks:
            # Insufficient evidence response
            content = "I could not find sufficient supporting information in the authorized matter documents."
        else:
            # Build grounded response with real citations from the context blocks
            referenced_chunks = []
            synthesized_facts = []

            for chunk_id, text in context_blocks[:3]:
                referenced_chunks.append(chunk_id.strip())
                clean_snippet = " ".join(text.strip().split()[:25])
                synthesized_facts.append(
                    f"Based on the authorized matter documents ({clean_snippet}...), the record demonstrates supporting evidence [CITATION:{chunk_id.strip()}]."
                )

            content = (
                "Based on the authorized legal matter records, the evidence reveals the following:\n\n"
                + "\n\n".join(synthesized_facts)
                + "\n\nConclusion: The above factual assertions are strictly grounded in the case files."
            )

        latency_ms = int((time.time() - start_time) * 1000)
        tokens_in = len(user_content.split())
        tokens_out = len(content.split())

        return LLMResponse(
            content=content,
            model=self.model,
            token_count_input=tokens_in,
            token_count_output=tokens_out,
            latency_ms=latency_ms,
        )
