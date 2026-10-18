from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Claim(BaseModel, Base):
    __tablename__ = "claims"

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    claim_type = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="active")

    matter = relationship("Matter", back_populates="claims")
