from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Event(BaseModel, Base):
    __tablename__ = "events"

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime(timezone=True), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, default="other")
    source_document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True
    )
    is_ai_generated = Column(Boolean, default=False, nullable=False)
    confidence = Column(Float, nullable=True)
    created_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    matter = relationship("Matter", back_populates="events")
