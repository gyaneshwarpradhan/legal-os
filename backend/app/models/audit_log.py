import uuid
from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True, index=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=True, index=True
    )
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    organization = relationship("Organization")
    user = relationship("User")
    matter = relationship("Matter")
