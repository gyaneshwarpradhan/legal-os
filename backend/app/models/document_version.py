import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False, index=True
    )
    version_number = Column(Integer, nullable=False, default=1)
    file_name = Column(String(500), nullable=False)
    storage_key = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    uploaded_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    document = relationship("Document", back_populates="versions")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
