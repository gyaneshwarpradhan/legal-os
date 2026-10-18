# SPDX-License-Identifier: MIT
"""Citation utilities for AI workflows.

The LLM providers (mock and production) embed citation markers in the generated
text using the syntax ``[DOCUMENT_CHUNK_ID:<uuid>]``.  These helpers locate the
markers, extract the referenced chunk IDs, and verify that the chunks belong to
the same matter as the request – a crucial guardrail to prevent cross‑matter
leakage.
"""

import re
from typing import List, Dict

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk

# Regular expression for citation markers.  The UUID capture group is case‑
# insensitive and allows hyphens.
_CITATION_RE = re.compile(r"\[DOCUMENT_CHUNK_ID:([0-9a-fA-F-]{36})\]")


def extract_citations(text: str) -> List[Dict[str, str]]:
    """Return a list of citation dictionaries found in *text*.

    Each dictionary contains the ``chunk_id`` (as a string) and the raw ``marker``
    that was present in the original text.  The marker is retained so callers can
    replace it with a richer UI element (e.g., a tooltip) if desired.
    """
    citations: List[Dict[str, str]] = []
    for match in _CITATION_RE.finditer(text):
        citations.append({
            "chunk_id": match.group(1),
            "marker": match.group(0),
        })
    return citations


def validate_citations(
    citations: List[Dict[str, str]],
    matter_id: str,
    db: Session,
) -> List[Dict[str, str]]:
    """Validate that every citation refers to a chunk belonging to *matter_id*.

    The function returns a filtered list containing only the *valid* citations.
    If an invalid citation is detected, it is omitted from the result – the
    caller can decide whether to surface a warning to the user.
    """
    if not citations:
        return []

    # Extract the unique chunk IDs from the list.
    chunk_ids = {c["chunk_id"] for c in citations}
    # Query the DB for chunks that match both the ID and the matter.
    valid_chunks = (
        db.query(DocumentChunk.id)
        .filter(DocumentChunk.id.in_(chunk_ids), DocumentChunk.matter_id == matter_id)
        .all()
    )
    valid_set = {str(row.id) for row in valid_chunks}
    # Keep only citations whose chunk_id is present in the valid set.
    return [c for c in citations if c["chunk_id"] in valid_set]
