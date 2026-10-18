from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Draft(BaseModel, Base):
    __tablename__ = "drafts"

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    ai_conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("ai_conversations.id"), nullable=True
    )
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    draft_type = Column(String(100), nullable=False, default="motion")
    status = Column(String(50), nullable=False, default="draft")  # draft, in_review, approved, rejected, finalized
    created_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    reviewed_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    matter = relationship("Matter")
    conversation = relationship("AIConversation")
    created_by = relationship("User", foreign_keys=[created_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
