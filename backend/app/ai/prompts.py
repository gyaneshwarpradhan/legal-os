# SPDX-License-Identifier: MIT
"""Prompt templates for AI workflows.

The system uses a *grounding* prompt that forces the model to reference only
authorised excerpts.  Citations are expected in the form
``[DOCUMENT_CHUNK_ID:<uuid>]`` and the model is instructed to place a citation
after every factual statement.

Two prompts are provided:

* ``GROUNDING_PROMPT`` – used for normal Q&A, summarisation and timeline
  extraction.  The ``{context}`` placeholder will be replaced with the retrieved
  document excerpts (concatenated text) before sending the request to the LLM.

* ``INSUFFICIENT_EVIDENCE_PROMPT`` – a fallback when the retrieval step does
  not return any relevant chunks.  The model should reply with a short
  apology/explanation and *no* citation markers.
"""

# The grounding prompt tells the model to answer based solely on the supplied
# excerpts and to cite each fact with a marker.
GROUNDING_PROMPT = """You are an AI legal assistant. Answer the user's question using **only** the following excerpts from the matter's documents. Cite each factual statement with a citation marker using the exact syntax ``[DOCUMENT_CHUNK_ID:<uuid>]`` where <uuid> is the ID of the source chunk.

If a piece of information is not present in the excerpts, do not fabricate it; instead, respond that the information is unavailable.

---
Context excerpts (provide as needed):\n{context}\n---\nUser question: {question}\n"""

# When no relevant documents are found, we ask the model to politely indicate
# lack of evidence without adding any citations.
INSUFFICIENT_EVIDENCE_PROMPT = """You are an AI legal assistant. The user asked a question, but no relevant documents were found in the matter's knowledge base. Respond politely that the information is not available, and do not include any citation markers.

User question: {question}\n"""
