# SPDX-License-Identifier: MIT
"""AI workflow for Question & Answer.

This module implements a simple QA workflow that:
1. Retrieves the most relevant document chunks for a user's query using the
   hybrid search implementation (`search.search_matter_knowledge`).
2. Builds a grounding prompt that forces the LLM to answer based only on those
   excerpts, with citation markers.
3. Calls the configured LLM provider (`get_llm_provider`).
4. Extracts citation markers from the LLM response, validates that they belong
   to the same matter, and returns a structured response.
"""

from typing import List, Dict

from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.providers import get_llm_provider
from app.ai.prompts import GROUNDING_PROMPT, INSUFFICIENT_EVIDENCE_PROMPT
from app.ai.citations import extract_citations, validate_citations
from app.services.search import search_matter_knowledge
from app.models.document_chunk import DocumentChunk
from app.core.database import get_db


def answer_question(
    *,
    matter_id: str,
    query: str,
    db: Session = Depends(get_db),
    top_k: int = 5,
) -> Dict:
    """Answer a user query with source‑grounded citations.

    Returns a dictionary with ``answer`` (the raw LLM text) and ``citations`` – a
    list of ``{"chunk_id": <uuid>, "snippet": <excerpt>}`` dictionaries for the
    validated citations.
    """
    # 1️⃣ Retrieve relevant chunks.
    chunks = search_matter_knowledge(
        db=db,
        matter_id=matter_id,
        query=query,
        limit=top_k,
        min_score=0.0,
    )

    if not chunks:
        # No relevant evidence – ask LLM to respond with an "insufficient
        # evidence" message.
        prompt = INSUFFICIENT_EVIDENCE_PROMPT.format(question=query)
        messages = [{"role": "user", "content": prompt}]
        provider = get_llm_provider()
        response = provider.generate(messages)
        return {"answer": response.content, "citations": []}

    # 2️⃣ Build context from the retrieved chunks.
    context_parts: List[str] = []
    for ch in chunks:
        # Include the chunk ID in the context so the model can reference it.
        context_parts.append(f"[CHUNK_ID:{ch.id}] {ch.content}")
    context = "\n\n".join(context_parts)

    # 3️⃣ Create grounding prompt.
    prompt = GROUNDING_PROMPT.format(context=context, question=query)
    messages = [{"role": "user", "content": prompt}]

    # 4️⃣ Call LLM.
    provider = get_llm_provider()
    llm_resp = provider.generate(messages)
    answer_text = llm_resp.content

    # 5️⃣ Extract and validate citations.
    raw_cits = extract_citations(answer_text)
    valid_cits = validate_citations(raw_cits, matter_id, db)

    # Build snippet for each citation (optional – we can fetch the chunk content).
    snippets: List[Dict] = []
    if valid_cits:
        # Load the chunk contents in a single query.
        chunk_ids = [c["chunk_id"] for c in valid_cits]
        chunk_map = (
            db.query(DocumentChunk.id, DocumentChunk.content)
            .filter(DocumentChunk.id.in_(chunk_ids))
            .all()
        )
        content_lookup = {str(cid): txt for cid, txt in chunk_map}
        for cit in valid_cits:
            snippets.append({
                "chunk_id": cit["chunk_id"],
                "snippet": content_lookup.get(cit["chunk_id"], ""),
            })

    return {"answer": answer_text, "citations": snippets}
