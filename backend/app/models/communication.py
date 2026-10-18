from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Communication(BaseModel, Base):
    __tablename__ = "communications"

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    communication_type = Column(String(50), nullable=False, default="email")
    direction = Column(String(50), nullable=False, default="internal")
    sender = Column(String(255), nullable=True)
    recipients = Column(JSON, nullable=True)
    date = Column(DateTime(timezone=True), nullable=False)
    source_integration = Column(String(100), nullable=True)
    created_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    matter = relationship("Matter")
    created_by = relationship("User", foreign_keys=[created_by_id])
