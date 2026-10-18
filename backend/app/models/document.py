from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Document(BaseModel, Base):
    __tablename__ = "documents"

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    title = Column(String(500), nullable=False)
    document_type = Column(String(100), nullable=False, default="other", index=True)
    file_name = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    storage_key = Column(String(1000), nullable=False)
    status = Column(String(50), nullable=False, default="uploading", index=True)
    processing_status = Column(JSON, nullable=True)
    uploaded_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    matter = relationship("Matter", back_populates="documents")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
    versions = relationship(
        "DocumentVersion", back_populates="document", cascade="all, delete-orphan"
    )
    chunks = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
