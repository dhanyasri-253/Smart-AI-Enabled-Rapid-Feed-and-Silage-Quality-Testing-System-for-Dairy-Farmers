"""
Pydantic Schemas for Quality Assessment
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class IndicatorItem(BaseModel):
    parameter: str
    measured_value: str
    reference_target: str
    status: str
    severity: str  # success, warning, danger, neutral
    explanation: str
    category: str


class AssessmentOut(BaseModel):
    id: int
    sample_id: int
    assessment_status: str
    quality_category: str
    quality_score: Optional[float] = None
    confidence: Optional[str] = None
    model_version: str
    recommendation: str
    parameter_breakdown: Optional[Any] = None
    lab_recommended: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentRunRequest(BaseModel):
    sample_id: int


class WarningSignItem(BaseModel):
    category: str
    category_ta: str
    severity: str  # success, warning, danger
    title: str
    title_ta: str
    description: str
    description_ta: str


class FarmerGuidanceRequest(BaseModel):
    crop: str = "Corn / Maize"
    harvest_timing: str = "Unknown"
    sealing_delay: str = "Unknown"
    storage_method: str = "Unknown"
    inoculant_used: str = "Unknown"
    visible_mould: str = "None"
    silage_color: str = "Normal"
    silage_odor: str = "Clean"
    temperature_feeling: str = "Cool"
    lab_report_available: bool = False
    ph: Optional[float] = None
    moisture: Optional[float] = None
    temperature: Optional[float] = None
    notes: Optional[str] = None
    save_sample: bool = False


class FarmerGuidanceResponse(BaseModel):
    mode: str = "farmer_guided"
    is_ml_prediction: bool = False
    disclaimer_en: str
    disclaimer_ta: str
    summary: Dict[str, Any]
    warning_signs: List[Dict[str, Any]]
    guidance_en: List[str]
    guidance_ta: List[str]
    lab_recommended: bool
    lab_reasons_en: List[str]
    lab_reasons_ta: List[str]
    referral_contacts_en: str
    referral_contacts_ta: str
    sample_id: Optional[str] = None
    db_id: Optional[int] = None

