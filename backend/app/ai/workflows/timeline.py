# SPDX-License-Identifier: MIT
"""AI workflow for timeline extraction.

Given a user query (typically a request to produce a timeline of events), the
workflow retrieves relevant chunks, builds a prompt asking the model to output an
ordered list of key dates/events with citations, and returns a structured
timeline.
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


def extract_timeline(
    *,
    matter_id: str,
    query: str,
    db: Session = Depends(get_db),
    top_k: int = 5,
) -> Dict:
    """Extract a timeline from the matter based on *query*.

    Returns a dictionary with ``timeline`` – a list of items ``{"date": <str>,
    "event": <str>, "citation": {"chunk_id": <uuid>, "snippet": <str>}}`` – and
    ``answer`` – the raw model response (useful for debugging).
    """
    # Search for relevant chunks.
    chunks = search_matter_knowledge(
        db=db,
        matter_id=matter_id,
        query=query,
        limit=top_k,
        min_score=0.0,
    )

    if not chunks:
        prompt = INSUFFICIENT_EVIDENCE_PROMPT.format(question=query)
        provider = get_llm_provider()
        resp = provider.generate([{"role": "user", "content": prompt}])
        return {"answer": resp.content, "timeline": []}

    # Build context.
    context_parts: List[str] = []
    for ch in chunks:
        context_parts.append(f"[CHUNK_ID:{ch.id}] {ch.content}")
    context = "\n\n".join(context_parts)

    # Prompt the model to produce a timeline.
    timeline_prompt = (
        "You are an AI legal assistant. Using ONLY the excerpts below, "
        "create an ordered timeline of the key dates/events relevant to the "
        "question. Each entry should be a JSON object with fields `date`, "
        "`event`, and must include a citation marker `[DOCUMENT_CHUNK_ID:<uuid>]` "
        "for the source. Return the timeline as a JSON array."
    )
    prompt = GROUNDING_PROMPT.format(context=context, question=timeline_prompt + "\n" + query)
    provider = get_llm_provider()
    llm_resp = provider.generate([{"role": "user", "content": prompt}])
    answer_text = llm_resp.content

    # Extract citations.
    raw_cits = extract_citations(answer_text)
    valid_cits = validate_citations(raw_cits, matter_id, db)

    # Build snippet lookup.
    snippet_lookup: Dict[str, str] = {}
    if valid_cits:
        ids = [c["chunk_id"] for c in valid_cits]
        chunk_map = (
            db.query(DocumentChunk.id, DocumentChunk.content)
            .filter(DocumentChunk.id.in_(ids))
            .all()
        )
        snippet_lookup = {str(cid): txt for cid, txt in chunk_map}

    # Attempt to parse JSON array from answer (best‑effort).
    timeline_items: List[Dict] = []
    try:
        import json
        # Find the first '[' and the matching ']'.
        start = answer_text.find('[')
        end = answer_text.rfind(']')
        if start != -1 and end != -1 and end > start:
            json_str = answer_text[start : end + 1]
            raw_items = json.loads(json_str)
            for item in raw_items:
                # Expect item to contain a citation marker; locate it.
                cit = None
                if isinstance(item, dict):
                    # Look for a citation marker in any string field.
                    for val in item.values():
                        if isinstance(val, str):
                            m = next(iter(extract_citations(val)), None)
                            if m:
                                cit = m
                                break
                if cit and cit["chunk_id"] in snippet_lookup:
                    citation_info = {"chunk_id": cit["chunk_id"], "snippet": snippet_lookup[cit["chunk_id"]]}
                else:
                    citation_info = None
                timeline_items.append({
                    "date": item.get("date") if isinstance(item, dict) else None,
                    "event": item.get("event") if isinstance(item, dict) else None,
                    "citation": citation_info,
                })
    except Exception:
        # Fallback: return empty timeline but keep raw answer.
        timeline_items = []

    return {"answer": answer_text, "timeline": timeline_items}
