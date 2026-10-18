from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Task(BaseModel, Base):
    __tablename__ = "tasks"

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="todo")
    priority = Column(String(50), nullable=False, default="medium")
    assigned_to_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    matter = relationship("Matter", back_populates="tasks")
