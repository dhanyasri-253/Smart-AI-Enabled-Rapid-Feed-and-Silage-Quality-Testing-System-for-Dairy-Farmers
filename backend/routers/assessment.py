from datetime import date
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.farmer import Farmer
from backend.models.sample import Sample
from backend.models.assessment import Assessment
from backend.schemas.assessment import AssessmentOut, AssessmentRunRequest, FarmerGuidanceRequest, FarmerGuidanceResponse
from backend.dependencies import get_current_farmer_optional
from backend.services.assessment_service import run_and_save_assessment
from backend.services.farmer_guidance_service import evaluate_farmer_mode

router = APIRouter(prefix="/api/assessment", tags=["Quality Assessment"])


@router.post("/farmer-guidance", response_model=FarmerGuidanceResponse)
def get_farmer_guidance(
    payload: FarmerGuidanceRequest,
    farmer: Optional[Farmer] = Depends(get_current_farmer_optional),
    db: Session = Depends(get_db)
):
    """
    Evaluates ordinary farmer sensory, harvest, and storage observations.
    Returns clear, practical feeding and storage guidance with validated warnings.
    Does NOT invoke the 11-feature ML pipeline and does NOT fabricate FQI predictions.
    Optionally saves the sample and screening record into the database for history tracking.
    """
    data = payload.model_dump()
    result = evaluate_farmer_mode(data)

    if payload.save_sample:
        if not farmer:
            farmer = db.query(Farmer).first()
            if not farmer:
                farmer = Farmer(
                    name="Demo Dairy Farmer",
                    mobile="9876543210",
                    location="Karnal, Haryana",
                    password_hash="demo"
                )
                db.add(farmer)
                db.commit()
                db.refresh(farmer)

        today = date.today()
        sample_code = f"SMP-{today.year}-{uuid.uuid4().hex[:5].upper()}"

        notes_content = (
            f"FARMER MODE: Harvest: {payload.harvest_timing} | Delay: {payload.sealing_delay} | "
            f"Storage: {payload.storage_method} | Additive: {payload.inoculant_used} | Mould: {payload.visible_mould}"
        )
        if payload.notes:
            notes_content += f" | Farmer Notes: {payload.notes}"

        new_sample = Sample(
            sample_id=sample_code,
            farmer_id=farmer.id,
            sample_type=payload.crop,
            sample_date=today,
            ph=payload.ph,
            moisture=payload.moisture,
            temperature=payload.temperature,
            visual_odor=payload.silage_odor,
            visual_color=payload.silage_color,
            notes=notes_content
        )
        db.add(new_sample)
        db.commit()
        db.refresh(new_sample)

        # Save assessment record linking to this sample
        new_assessment = Assessment(
            sample_id=new_sample.id,
            assessment_status="Completed",
            quality_category="Farmer Mode — Rule-Based Guidance (Non-ML)",
            quality_score=None,  # Intentionally null: No ML FQI generated without lab report
            confidence="ICAR-NDRI Agronomic Benchmarks (Farmer Screening)",
            model_version="Agronomic-Rules-v1.0 (Non-ML)",
            recommendation="\n\n".join(result["guidance_en"]),
            parameter_breakdown=result,
            lab_recommended=result["lab_recommended"]
        )
        db.add(new_assessment)
        db.commit()

        result["sample_id"] = sample_code
        result["db_id"] = new_sample.id

    return result


@router.post("", response_model=AssessmentOut)
def trigger_assessment(payload: AssessmentRunRequest, db: Session = Depends(get_db)):
    """
    Triggers or recalculates quality assessment for a sample.
    """
    sample = db.query(Sample).filter(Sample.id == payload.sample_id).first()
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found.")
        
    assessment = run_and_save_assessment(sample, db)
    return assessment


@router.get("/{sample_id}", response_model=AssessmentOut)
def get_assessment_by_sample(sample_id: int, db: Session = Depends(get_db)):
    """
    Returns the assessment record for a given sample.
    """
    assessment = db.query(Assessment).filter(Assessment.sample_id == sample_id).first()
    if not assessment:
        sample = db.query(Sample).filter(Sample.id == sample_id).first()
        if not sample:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found.")
        assessment = run_and_save_assessment(sample, db)
        
    return assessment

