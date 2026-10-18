from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModel


class Expert(BaseModel, Base):
    __tablename__ = "experts"

    matter_id = Column(
        UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False, index=True
    )
    name = Column(String(500), nullable=False)
    specialty = Column(String(255), nullable=False)
    organization_name = Column(String(255), nullable=True)
    contact_info = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    retained_by = Column(String(50), nullable=False, default="plaintiff")

    matter = relationship("Matter", back_populates="experts")
