from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Witness(BaseModel, Base):
    __tablename__ = "witnesses"

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    name = Column(String(500), nullable=False)
    witness_type = Column(String(50), nullable=False, default="fact")
    description = Column(Text, nullable=True)
    contact_info = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)

    matter = relationship("Matter", back_populates="witnesses")
