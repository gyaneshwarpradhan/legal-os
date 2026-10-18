import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_conversations.id"),
        nullable=False,
        index=True,
    )
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=True)
    token_count_input = Column(Integer, nullable=True)
    token_count_output = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    conversation = relationship("AIConversation", back_populates="messages")
    citations = relationship(
        "Citation", back_populates="ai_message", cascade="all, delete-orphan"
    )
