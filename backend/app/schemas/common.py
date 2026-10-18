from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "0.1.0"


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[Any]  # Will be overridden in concrete usage
    total: int
    page: int
    page_size: int
