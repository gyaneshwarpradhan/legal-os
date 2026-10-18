"""Embedding provider abstraction with deterministic vector generation."""
import hashlib
import math
import os
from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding vector for a single text chunk."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of text chunks."""
        pass


class LocalDeterministicEmbeddingProvider(EmbeddingProvider):
    """
    Zero-dependency deterministic embedding generator (128 dimensions).
    Uses n-gram bag of hashes with L2 unit normalization.
    Ensures cosine similarity works natively and reliably in any test/offline environment.
    """

    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        vec = [0.0] * self.dimension
        clean_text = text.lower()
        words = clean_text.split()

        # Word unigrams and character trigrams
        tokens = words + [clean_text[i : i + 3] for i in range(len(clean_text) - 2)]

        for token in tokens:
            # Deterministic hash bucket
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            # Sign bit from second byte
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign

        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        else:
            vec = [1.0 / math.sqrt(self.dimension)] * self.dimension

        return vec

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI text-embedding-3-small integration."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model

    def embed_text(self, text: str) -> List[float]:
        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"input": text, "model": self.model}
        resp = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers,
            json=payload,
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"input": texts, "model": self.model}
        resp = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers,
            json=payload,
            timeout=60.0,
        )
        resp.raise_for_status()
        data = sorted(resp.json()["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in data]


def get_embedding_provider() -> EmbeddingProvider:
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return OpenAIEmbeddingProvider(api_key=openai_key)
    return LocalDeterministicEmbeddingProvider()


embedding_provider = get_embedding_provider()
