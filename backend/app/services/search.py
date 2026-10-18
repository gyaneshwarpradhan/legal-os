"""Hybrid search engine combining keyword ranking and vector cosine similarity with strict matter isolation."""
import math
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embeddings import embedding_provider


@dataclass
class SearchResult:
    chunk_id: UUID
    document_id: UUID
    document_title: str
    page_number: Optional[int]
    content: str
    score: float
    match_type: str


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm1 * norm2)))


def search_matter_knowledge(
    db: Session,
    matter_id: UUID,
    query: str,
    limit: int = 10,
    min_score: float = 0.15,
) -> List[SearchResult]:
    """
    Search chunks strictly within the specified matter_id.
    Zero cross-case leakage is enforced by the hard matter_id filter.
    """
    query_clean = query.strip()
    if not query_clean:
        return []

    # 1. Generate query embedding
    query_vector = embedding_provider.embed_text(query_clean)

    # 2. Fetch all candidate chunks for this matter
    # Strict matter-level quarantine:
    candidates = (
        db.query(DocumentChunk, Document.title)
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(
            DocumentChunk.matter_id == matter_id,
            Document.is_deleted == False,
        )
        .all()
    )

    if not candidates:
        return []

    query_terms = [t.lower() for t in query_clean.split() if len(t) > 2]
    results = []

    for chunk, doc_title in candidates:
        content_lower = chunk.content.lower()

        # Keyword match scoring (0.0 to 1.0)
        keyword_hits = sum(1 for term in query_terms if term in content_lower)
        keyword_score = (
            min(1.0, keyword_hits / len(query_terms)) if query_terms else 0.0
        )

        # Semantic cosine similarity
        chunk_vector = None
        if chunk.metadata_ and isinstance(chunk.metadata_, dict):
            chunk_vector = chunk.metadata_.get("embedding")

        semantic_score = 0.0
        if chunk_vector:
            semantic_score = cosine_similarity(query_vector, chunk_vector)

        # Hybrid weighting (60% semantic, 40% keyword)
        combined_score = (0.6 * semantic_score) + (0.4 * keyword_score)

        if combined_score >= min_score or keyword_hits > 0:
            match_type = "hybrid" if (keyword_score > 0 and semantic_score > 0) else (
                "keyword" if keyword_score > semantic_score else "semantic"
            )
            results.append(
                SearchResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    document_title=doc_title,
                    page_number=chunk.page_number,
                    content=chunk.content,
                    score=round(combined_score, 4),
                    match_type=match_type,
                )
            )

    # Sort descending by score
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:limit]
