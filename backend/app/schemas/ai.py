from pydantic import BaseModel, Field
from typing import List, Optional

class AIAskRequest(BaseModel):
    """Payload for AI question answering."""
    question: str = Field(..., description="The user question to answer")

class Citation(BaseModel):
    """Simplified citation object returned to the client."""
    chunk_id: str = Field(..., description="UUID of the referenced DocumentChunk")
    marker: str = Field(..., description="Raw citation marker as produced by the LLM")

class AIAskResponse(BaseModel):
    answer: str = Field(..., description="Generated answer text")
    citations: List[Citation] = Field(default_factory=list, description="Citations referenced in the answer")

class AISummarizeRequest(BaseModel):
    """Payload for document summarisation. Currently no extra fields, but kept for extensibility."""
    pass

class AISummarizeResponse(BaseModel):
    summary: str = Field(..., description="Generated summary text")
    citations: List[Citation] = Field(default_factory=list, description="Citations referenced in the summary")

class AITimelineRequest(BaseModel):
    """Payload for timeline extraction.

    ``query`` is a natural‑language description of the timeline the user wants, e.g.
    "Give me all filing and hearing dates for this case".
    """
    query: str = Field(..., description="User query describing the desired timeline")

class TimelineEvent(BaseModel):
    date: str = Field(..., description="ISO‑8601 date string of the event")
    description: str = Field(..., description="Human‑readable description of the event")
    # Optional additional fields could be added (e.g., source document ID)

class AITimelineResponse(BaseModel):
    timeline: List[TimelineEvent] = Field(default_factory=list, description="Ordered list of timeline events")
    citations: List[Citation] = Field(default_factory=list, description="Citations referenced in the timeline generation")
