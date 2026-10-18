from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class AIConversation(BaseModel, Base):
    __tablename__ = "ai_conversations"

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    title = Column(String(500), nullable=True)
    workflow_type = Column(String(100), nullable=False, default="matter_qa")

    matter = relationship("Matter")
    user = relationship("User")
    messages = relationship(
        "AIMessage", back_populates="conversation", cascade="all, delete-orphan"
    )
