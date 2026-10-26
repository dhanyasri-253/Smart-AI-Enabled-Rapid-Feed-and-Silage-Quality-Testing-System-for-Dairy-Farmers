"""
Assessment Service for SmartSilageAI (SIH26111)
Coordinates feature validation, ML / Heuristic assessment, and database persistence.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.sample import Sample
from backend.models.assessment import Assessment
from backend.ml.predictor import predict_quality


def run_and_save_assessment(sample: Sample, db: Session) -> Assessment:
    """
    Executes rapid preliminary quality screening on a sample and saves/updates assessment.
    """
    sample_dict = {
        "sample_type": sample.sample_type,
        "ph": sample.ph,
        "moisture": sample.moisture,
        "temperature": sample.temperature,
        "crude_protein": sample.crude_protein,
        "ndf": sample.ndf,
        "adf": sample.adf,
        "ash": sample.ash,
        "visual_odor": sample.visual_odor,
        "visual_color": sample.visual_color,
    }
    
    # Run prediction / heuristic screening
    screening_result = predict_quality(sample_dict)
    
    # Check if an assessment already exists for this sample
    existing = db.query(Assessment).filter(Assessment.sample_id == sample.id).first()
    
    if existing:
        existing.assessment_status = "Completed"
        existing.quality_category = screening_result.get("quality_category", "Prototype — AI model pending validation")
        existing.quality_score = screening_result.get("quality_score")
        existing.confidence = screening_result.get("confidence")
        existing.model_version = screening_result.get("model_version", "Heuristic-v1.0 (ML Model Pending)")
        existing.recommendation = "\n\n".join(screening_result.get("recommendations", []))
        existing.parameter_breakdown = screening_result
        existing.lab_recommended = screening_result.get("lab_recommended", True)
        db.commit()
        db.refresh(existing)
        return existing
    
    new_assessment = Assessment(
        sample_id=sample.id,
        assessment_status="Completed",
        quality_category=screening_result.get("quality_category", "Prototype — AI model pending validation"),
        quality_score=screening_result.get("quality_score"),
        confidence=screening_result.get("confidence"),
        model_version=screening_result.get("model_version", "Heuristic-v1.0 (ML Model Pending)"),
        recommendation="\n\n".join(screening_result.get("recommendations", [])),
        parameter_breakdown=screening_result,
        lab_recommended=screening_result.get("lab_recommended", True),
    )
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)
    return new_assessment
