"""
Dashboard Router for SmartSilageAI (SIH26111)
Aggregates summary statistics for farmers, extension officers, and jury demonstrations.
"""
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.database import get_db
from backend.models.farmer import Farmer
from backend.models.sample import Sample
from backend.models.assessment import Assessment
from backend.dependencies import get_current_farmer_optional
from backend.ml.model_loader import get_model_status

router = APIRouter(prefix="/api/dashboard", tags=["Farmer Dashboard"])


@router.get("")
def get_dashboard_summary(
    farmer: Farmer = Depends(get_current_farmer_optional),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns high-level statistics for the dashboard view.
    """
    query = db.query(Sample)
    if farmer:
        query = query.filter(Sample.farmer_id == farmer.id)
        
    total_samples = query.count()
    
    # Silage vs other feed types
    silage_samples = query.filter(Sample.sample_type.ilike("%Silage%")).count()
    feed_samples = total_samples - silage_samples
    
    # Samples requiring attention (lab recommended or spoilage signs)
    attention_query = query.join(Assessment, Sample.id == Assessment.sample_id).filter(Assessment.lab_recommended == True)
    attention_count = attention_query.count()
    
    # Recent 5 samples
    recent = query.order_by(desc(Sample.created_at)).limit(5).all()
    recent_list = []
    for s in recent:
        recent_list.append({
            "id": s.id,
            "sample_id": s.sample_id,
            "sample_type": s.sample_type,
            "sample_date": s.sample_date.isoformat(),
            "ph": s.ph,
            "moisture": s.moisture,
            "temperature": s.temperature,
            "quality_score": s.assessment.quality_score if s.assessment else None,
            "lab_recommended": s.assessment.lab_recommended if s.assessment else True,
            "category": s.assessment.quality_category if s.assessment else "Pending",
        })
        
    return {
        "farmer_name": farmer.name if farmer else "Dairy Farmer (Demo Mode)",
        "total_samples": total_samples,
        "silage_samples": silage_samples,
        "feed_samples": feed_samples,
        "attention_needed": attention_count,
        "model_status": get_model_status(),
        "recent_samples": recent_list,
    }
