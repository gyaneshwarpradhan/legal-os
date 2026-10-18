from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Organization(BaseModel, Base):
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="organization", lazy="dynamic")
    matters = relationship("Matter", back_populates="organization", lazy="dynamic")
