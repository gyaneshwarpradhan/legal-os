from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Party(BaseModel, Base):
    __tablename__ = "parties"

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    name = Column(String(500), nullable=False)
    party_type = Column(String(50), nullable=False, default="plaintiff")
    entity_type = Column(String(50), nullable=False, default="individual")
    description = Column(Text, nullable=True)
    contact_info = Column(JSON, nullable=True)

    matter = relationship("Matter", back_populates="parties")
