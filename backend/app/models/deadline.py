from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Deadline(BaseModel, Base):
    __tablename__ = "deadlines"

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    deadline_type = Column(String(50), nullable=False, default="internal")
    status = Column(String(50), nullable=False, default="pending")
    is_high_risk = Column(Boolean, default=False, nullable=False)
    requires_review = Column(Boolean, default=False, nullable=False)
    assigned_to_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    matter = relationship("Matter", back_populates="deadlines")
