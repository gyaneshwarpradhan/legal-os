from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class User(BaseModel, Base):
    __tablename__ = "users"

    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    email = Column(String(320), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="attorney")
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    matter_memberships = relationship("MatterMember", back_populates="user", foreign_keys="MatterMember.user_id")
