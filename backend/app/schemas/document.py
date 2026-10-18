from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    title: str
    document_type: str
    file_name: str
    file_type: str
    file_size: int
    status: str
    processing_status: Optional[Dict[str, Any]] = None
    created_at: datetime


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    matter_id: UUID
    chunk_index: int
    content: str
    page_number: Optional[int] = None
    token_count: Optional[int] = None
    created_at: datetime


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10


class SearchResultResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_title: str
    page_number: Optional[int] = None
    content: str
    score: float
    match_type: str


class ReclassifyRequest(BaseModel):
    document_type: str
