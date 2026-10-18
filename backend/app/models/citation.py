import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Citation(Base):
    """
    First-class Citation entity.
    Every grounded AI response links directly to the specific Document and DocumentChunk.
    """
    __tablename__ = "citations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    ai_message_id = Column(
        UUID(as_uuid=True), ForeignKey("ai_messages.id"), nullable=False, index=True
    )
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True
    )
    document_chunk_id = Column(
        UUID(as_uuid=True),
        ForeignKey("document_chunks.id"),
        nullable=True,
        index=True,
    )
    page_number = Column(Integer, nullable=True)
    passage = Column(Text, nullable=True)
    relevance_score = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    ai_message = relationship("AIMessage", back_populates="citations")
    document = relationship("Document")
    document_chunk = relationship("DocumentChunk")
