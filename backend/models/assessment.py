"""
Assessment SQLAlchemy model for SmartSilageAI (SIH26111)
Records rapid preliminary screening outcome, explainable indicators, and recommendations.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sample_id = Column(Integer, ForeignKey("samples.id", ondelete="CASCADE"), nullable=False, unique=True)
    assessment_status = Column(String(50), nullable=False, default="Completed")
    quality_category = Column(String(80), nullable=False, default="Prototype — AI model pending validation")
    quality_score = Column(Float, nullable=True)
    confidence = Column(String(80), nullable=True, default="Field Reference Screening (Pre-ML Validation)")
    model_version = Column(String(100), nullable=False, default="Heuristic-v1.0 (ML Model Pending)")
    recommendation = Column(Text, nullable=False)
    parameter_breakdown = Column(JSON, nullable=True)
    lab_recommended = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sample = relationship("Sample", back_populates="assessment")
