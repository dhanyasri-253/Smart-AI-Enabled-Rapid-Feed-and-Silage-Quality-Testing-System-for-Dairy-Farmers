"""
Sample SQLAlchemy model for SmartSilageAI (SIH26111)
Stores feed and silage submissions, measurements, sensory cues, and image references.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sample_id = Column(String(50), unique=True, index=True, nullable=False)
    farmer_id = Column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    sample_type = Column(String(80), nullable=False)
    sample_date = Column(Date, default=date.today, nullable=False)

    # Field-level accessible measurements
    ph = Column(Float, nullable=True)
    moisture = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)

    # Optional laboratory measurements
    crude_protein = Column(Float, nullable=True)
    ndf = Column(Float, nullable=True)
    adf = Column(Float, nullable=True)
    ash = Column(Float, nullable=True)

    # Sensory & Visual Observations
    visual_odor = Column(String(60), nullable=True)
    visual_color = Column(String(60), nullable=True)

    # Media & Notes
    image_path = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    farmer = relationship("Farmer", back_populates="samples")
    assessment = relationship("Assessment", back_populates="sample", uselist=False, cascade="all, delete-orphan")
