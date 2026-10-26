"""
Farmer SQLAlchemy model for SmartSilageAI (SIH26111)
Represents dairy farmers, extension workers, or cooperative staff.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    mobile = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(120), nullable=True)
    location = Column(String(150), nullable=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    samples = relationship("Sample", back_populates="farmer", cascade="all, delete-orphan")
