"""
Pydantic Schemas for Sample Submission and History
"""
from datetime import datetime, date
from typing import Optional, Any
from pydantic import BaseModel, Field
from backend.schemas.assessment import AssessmentOut


class SampleCreate(BaseModel):
    sample_type: str = Field(..., example="Corn Silage")
    sample_date: Optional[date] = None

    # Field-level measurements
    ph: Optional[float] = Field(None, ge=2.0, le=12.0, example=3.9)
    moisture: Optional[float] = Field(None, ge=5.0, le=95.0, example=65.0)
    temperature: Optional[float] = Field(None, ge=0.0, le=80.0, example=26.0)

    # Optional laboratory measurements
    crude_protein: Optional[float] = Field(None, ge=0.0, le=50.0, example=8.5)
    ndf: Optional[float] = Field(None, ge=5.0, le=90.0, example=44.0)
    adf: Optional[float] = Field(None, ge=5.0, le=75.0, example=27.0)
    ash: Optional[float] = Field(None, ge=0.5, le=35.0, example=5.0)

    # Visual / sensory observations
    visual_odor: Optional[str] = Field(None, example="Pleasant / Fruity Acidic")
    visual_color: Optional[str] = Field(None, example="Olive Green / Light Brown")
    notes: Optional[str] = Field(None, max_length=1000, example="Pit silage packed in bunker.")


class SampleOut(BaseModel):
    id: int
    sample_id: str
    farmer_id: int
    sample_type: str
    sample_date: date
    ph: Optional[float] = None
    moisture: Optional[float] = None
    temperature: Optional[float] = None
    crude_protein: Optional[float] = None
    ndf: Optional[float] = None
    adf: Optional[float] = None
    ash: Optional[float] = None
    visual_odor: Optional[str] = None
    visual_color: Optional[str] = None
    image_path: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    assessment: Optional[AssessmentOut] = None

    class Config:
        from_attributes = True


class SampleHistorySummary(BaseModel):
    id: int
    sample_id: str
    sample_type: str
    sample_date: date
    ph: Optional[float] = None
    moisture: Optional[float] = None
    temperature: Optional[float] = None
    image_path: Optional[str] = None
    assessment_status: Optional[str] = None
    quality_category: Optional[str] = None
    quality_score: Optional[float] = None
    recommendation_preview: Optional[str] = None
    lab_recommended: Optional[bool] = None
