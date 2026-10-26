"""
Samples Router for SmartSilageAI (SIH26111)
Handles sample registration, measurement validation, optional image upload, and history listings.
"""
import os
import uuid
import shutil
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from backend.database import get_db
from backend.models.farmer import Farmer
from backend.models.sample import Sample
from backend.models.assessment import Assessment
from backend.schemas.sample import SampleOut, SampleHistorySummary
from backend.dependencies import get_current_farmer, get_current_farmer_optional
from backend.services.assessment_service import run_and_save_assessment
from backend.ml.preprocessing import validate_feature_bounds

router = APIRouter(prefix="/api/samples", tags=["Feed & Silage Samples"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("", response_model=SampleOut, status_code=status.HTTP_201_CREATED)
async def create_sample(
    sample_type: str = Form(...),
    sample_date: Optional[str] = Form(None),
    ph: Optional[float] = Form(None),
    moisture: Optional[float] = Form(None),
    temperature: Optional[float] = Form(None),
    crude_protein: Optional[float] = Form(None),
    ndf: Optional[float] = Form(None),
    adf: Optional[float] = Form(None),
    ash: Optional[float] = Form(None),
    visual_odor: Optional[str] = Form(None),
    visual_color: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    farmer: Optional[Farmer] = Depends(get_current_farmer_optional),
    db: Session = Depends(get_db)
):
    """
    Submits a new feed or silage sample with optional image and field/laboratory measurements.
    Instantly runs preliminary quality screening so the farmer gets immediate rapid feedback.
    """
    # Fallback to demo farmer if unauthenticated in demo mode
    if not farmer:
        farmer = db.query(Farmer).first()
        if not farmer:
            # Create default demo farmer
            farmer = Farmer(
                name="Demo Dairy Farmer",
                mobile="9876543210",
                location="Karnal, Haryana",
                password_hash="demo"
            )
            db.add(farmer)
            db.commit()
            db.refresh(farmer)

    # Validate physical parameter bounds
    raw_dict = {
        "ph": ph,
        "moisture": moisture,
        "temperature": temperature,
        "crude_protein": crude_protein,
        "ndf": ndf,
        "adf": adf,
        "ash": ash,
    }
    is_valid, err_msg = validate_feature_bounds(raw_dict)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)

    # Handle image upload if provided
    stored_image_path = None
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format ({ext}). Please upload JPG, JPEG, or PNG."
            )
        filename = f"sample_{uuid.uuid4().hex[:8]}_{int(date.today().strftime('%Y%m%d'))}{ext}"
        target_path = os.path.join(UPLOAD_DIR, filename)
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        stored_image_path = f"/uploads/{filename}"

    # Generate unique human-readable Sample ID
    s_date = date.fromisoformat(sample_date) if sample_date else date.today()
    sample_code = f"SMP-{s_date.year}-{uuid.uuid4().hex[:5].upper()}"

    new_sample = Sample(
        sample_id=sample_code,
        farmer_id=farmer.id,
        sample_type=sample_type.strip(),
        sample_date=s_date,
        ph=ph,
        moisture=moisture,
        temperature=temperature,
        crude_protein=crude_protein,
        ndf=ndf,
        adf=adf,
        ash=ash,
        visual_odor=visual_odor,
        visual_color=visual_color,
        image_path=stored_image_path,
        notes=notes.strip() if notes else None
    )
    db.add(new_sample)
    db.commit()
    db.refresh(new_sample)

    # Immediately trigger rapid screening assessment
    run_and_save_assessment(new_sample, db)
    db.refresh(new_sample)

    return new_sample


@router.get("", response_model=List[SampleHistorySummary])
def list_samples(
    sample_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    attention_only: Optional[bool] = Query(False),
    farmer: Optional[Farmer] = Depends(get_current_farmer_optional),
    db: Session = Depends(get_db)
):
    """
    Returns historical samples with filtering and search options.
    """
    query = db.query(Sample).order_by(desc(Sample.created_at))
    
    # Filter by farmer if authenticated
    if farmer:
        query = query.filter(Sample.farmer_id == farmer.id)
        
    if sample_type and sample_type != "All":
        query = query.filter(Sample.sample_type == sample_type)
        
    if search:
        search_fmt = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Sample.sample_id.ilike(search_fmt),
                Sample.notes.ilike(search_fmt),
                Sample.sample_type.ilike(search_fmt)
            )
        )
        
    samples = query.limit(100).all()
    
    results = []
    for s in samples:
        assessment = s.assessment
        q_cat = assessment.quality_category if assessment else "Pending Assessment"
        q_score = assessment.quality_score if assessment else None
        rec_prev = assessment.recommendation[:120] + "..." if assessment and assessment.recommendation else "No recommendation available."
        lab_rec = assessment.lab_recommended if assessment else True

        if attention_only and (not assessment or not assessment.lab_recommended):
            continue

        results.append(SampleHistorySummary(
            id=s.id,
            sample_id=s.sample_id,
            sample_type=s.sample_type,
            sample_date=s.sample_date,
            ph=s.ph,
            moisture=s.moisture,
            temperature=s.temperature,
            image_path=s.image_path,
            assessment_status=assessment.assessment_status if assessment else "Pending",
            quality_category=q_cat,
            quality_score=q_score,
            recommendation_preview=rec_prev,
            lab_recommended=lab_rec,
        ))
        
    return results


@router.get("/{sample_id_or_code}", response_model=SampleOut)
def get_sample_detail(sample_id_or_code: str, db: Session = Depends(get_db)):
    """
    Retrieves complete details of a sample, including all measurements and assessment breakdown.
    """
    if sample_id_or_code.isdigit():
        sample = db.query(Sample).filter(Sample.id == int(sample_id_or_code)).first()
    else:
        sample = db.query(Sample).filter(Sample.sample_id == sample_id_or_code.strip()).first()
        
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found.")
        
    # Ensure assessment is present; if missing, calculate it now
    if not sample.assessment:
        run_and_save_assessment(sample, db)
        db.refresh(sample)
        
    return sample


@router.delete("/{sample_id}", status_code=status.HTTP_200_OK)
def delete_sample(sample_id: int, db: Session = Depends(get_db)):
    """Deletes a sample and its associated assessment."""
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample not found.")
    db.delete(sample)
    db.commit()
    return {"status": "success", "message": f"Sample {sample.sample_id} successfully deleted."}
