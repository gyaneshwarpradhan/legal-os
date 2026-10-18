import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True
    )
    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    # Note: pgvector embedding column will be added in Phase 2
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    document = relationship("Document", back_populates="chunks")
    matter = relationship("Matter")
