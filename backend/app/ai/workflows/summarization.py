# SPDX-License-Identifier: MIT
"""AI workflow for document summarisation.

The workflow retrieves all chunks for a given document, builds a prompt that asks the
LLM to produce a concise summary while citing each factual statement.  It then
extracts and validates citations in the same way as the QA workflow.
"""

from typing import List, Dict

from fastapi import Depends
from sqlalchemy.orm import Session

from app.ai.providers import get_llm_provider
from app.ai.prompts import GROUNDING_PROMPT, INSUFFICIENT_EVIDENCE_PROMPT
from app.ai.citations import extract_citations, validate_citations
from app.services.search import search_matter_knowledge
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.core.database import get_db


def summarize_document(
    *,
    matter_id: str,
    document_id: str,
    db: Session = Depends(get_db),
) -> Dict:
    """Generate a summary of *document_id* with source citations.

    Returns ``{"summary": <str>, "citations": [{"chunk_id": <uuid>, "snippet": <str>} ]}``.
    """
    # Verify the document belongs to the requested matter.
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.matter_id == matter_id)
        .first()
    )
    if not doc:
        return {"summary": "Document not found or not accessible.", "citations": []}

    # Retrieve all chunks for this document (ordered by index).
    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id, DocumentChunk.matter_id == matter_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )
    if not chunks:
        # No content – let LLM respond with insufficient evidence.
        prompt = INSUFFICIENT_EVIDENCE_PROMPT.format(question="Summarise the document.")
        provider = get_llm_provider()
        resp = provider.generate([{"role": "user", "content": prompt}])
        return {"summary": resp.content, "citations": []}

    # Build context string with each chunk prefixed by its ID.
    context_parts: List[str] = []
    for ch in chunks:
        context_parts.append(f"[CHUNK_ID:{ch.id}] {ch.content}")
    context = "\n\n".join(context_parts)

    # Prompt the model to summarise using the grounding prompt.
    prompt = GROUNDING_PROMPT.format(context=context, question="Please provide a concise summary of the above document. Include citations for each factual statement.")
    provider = get_llm_provider()
    llm_resp = provider.generate([{"role": "user", "content": prompt}])
    answer_text = llm_resp.content

    # Extract and validate citations.
    raw_cits = extract_citations(answer_text)
    valid_cits = validate_citations(raw_cits, matter_id, db)

    # Resolve snippets for each citation.
    snippets: List[Dict] = []
    if valid_cits:
        ids = [c["chunk_id"] for c in valid_cits]
        chunk_map = (
            db.query(DocumentChunk.id, DocumentChunk.content)
            .filter(DocumentChunk.id.in_(ids))
            .all()
        )
        lookup = {str(cid): txt for cid, txt in chunk_map}
        for cit in valid_cits:
            snippets.append({"chunk_id": cit["chunk_id"], "snippet": lookup.get(cit["chunk_id"], "")})

    return {"summary": answer_text, "citations": snippets}
