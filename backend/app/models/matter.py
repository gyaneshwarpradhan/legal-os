from sqlalchemy import Boolean, Column, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Matter(BaseModel, Base):
    __tablename__ = "matters"

    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    case_number = Column(String(100), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    matter_type = Column(String(100), nullable=False, default="other")
    status = Column(String(50), nullable=False, default="active", index=True)
    date_opened = Column(Date, nullable=False)
    date_closed = Column(Date, nullable=True)
    court = Column(String(255), nullable=True)
    jurisdiction = Column(String(255), nullable=True)
    judge = Column(String(255), nullable=True)
    created_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="matters")
    created_by = relationship("User", foreign_keys=[created_by_id])
    members = relationship("MatterMember", back_populates="matter", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="matter", lazy="dynamic")
    parties = relationship("Party", back_populates="matter", cascade="all, delete-orphan")
    witnesses = relationship("Witness", back_populates="matter", cascade="all, delete-orphan")
    experts = relationship("Expert", back_populates="matter", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="matter", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="matter", cascade="all, delete-orphan")
    deadlines = relationship("Deadline", back_populates="matter", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="matter", cascade="all, delete-orphan")
