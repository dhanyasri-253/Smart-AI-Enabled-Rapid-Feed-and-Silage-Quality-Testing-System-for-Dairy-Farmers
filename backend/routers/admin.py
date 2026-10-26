"""
Admin & Technical Verification Router for SmartSilageAI (SIH26111)
Provides technical diagnostic visibility for SIH jury and agricultural research officers.
Explicitly confirms dataset & model status without false claims.
"""
from typing import Dict, Any
from fastapi import APIRouter
from backend.database import active_db_engine_name, DB_NAME, DB_HOST, DB_PORT
from backend.ml.model_loader import get_model_status
from backend.ml.predictor import evaluate_heuristics, REFERENCE_BENCHMARKS
from backend.ml.preprocessing import preprocess_sample_features

router = APIRouter(prefix="/api/admin", tags=["Technical / SIH Jury View"])


@router.get("/status")
def get_technical_system_status() -> Dict[str, Any]:
    """
    Returns verified technical status of the prototype.
    Ensures complete transparency for Smart India Hackathon evaluators.
    """
    model_info = get_model_status()
    
    return {
        "problem_statement": "SIH26111 — Smart AI-Enabled Rapid Feed and Silage Quality Testing System for Dairy Farmers",
        "ministry": "Ministry of Fisheries, Animal Husbandry & Dairying",
        "prototype_version": "1.0.0-SIH-Prototype",
        
        # Mandatory SIH transparency indicators
        "dataset_status": "Pending (No fabricated/synthetic data used)",
        "model_status": model_info["model_status"],
        "model_version": model_info["model_version"],
        "validation_status": "Pending Scientific Trials with ICAR-NDRI / Veterinary Universities",
        
        # Technical infrastructure details
        "active_database": {
            "engine": active_db_engine_name,
            "database": DB_NAME,
            "host": DB_HOST,
            "port": DB_PORT,
        },
        "ml_pipeline": {
            "loader": "backend.ml.model_loader",
            "preprocessor": "backend.ml.preprocessing",
            "predictor": "backend.ml.predictor",
            "target_model_file": model_info["model_path"],
            "model_loaded": model_info["model_loaded"],
        },
        "supported_sample_types": list(REFERENCE_BENCHMARKS.keys()),
        "science_benchmarks_reference": "ICAR-NDRI Guidelines for Ensiling & Quality Evaluation of Forages",
    }


@router.post("/test-pipeline")
def test_ml_pipeline_dry_run() -> Dict[str, Any]:
    """
    Executes a dry-run test through the preprocessing and predictor pipeline.
    Validates that the pipeline is ready to consume future trained models or heuristic rules.
    """
    test_sample = {
        "sample_type": "Corn Silage",
        "ph": 4.0,
        "moisture": 66.0,
        "temperature": 27.5,
        "crude_protein": 8.4,
        "ndf": 43.5,
        "adf": 26.0,
        "ash": 4.9,
        "visual_odor": "Pleasant / Fruity Acidic",
        "visual_color": "Olive Green / Light Brown",
    }
    
    processed = preprocess_sample_features(test_sample)
    output = evaluate_heuristics(processed)
    
    return {
        "status": "Pipeline Operational",
        "test_input": test_sample,
        "processed_features": processed,
        "pipeline_output": output,
    }
