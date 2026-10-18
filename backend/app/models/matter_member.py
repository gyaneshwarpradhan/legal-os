from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class MatterMember(BaseModel, Base):
    __tablename__ = "matter_members"
    __table_args__ = (
        UniqueConstraint("matter_id", "user_id", name="uq_matter_member"),
    )

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    role = Column(String(50), nullable=False, default="attorney")
    added_by_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Relationships
    matter = relationship("Matter", back_populates="members")
    user = relationship("User", back_populates="matter_memberships", foreign_keys=[user_id])
    added_by = relationship("User", foreign_keys=[added_by_id])
