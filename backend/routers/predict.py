"""
FastAPI router for FQI prediction endpoint (SIH26111).
Loads frozen scikit-learn pipeline (fqi_model.joblib) and evaluates raw inputs.
Supports both /predict and /api/predict paths under a single router registration.
"""

import logging
import os
from typing import Optional

import joblib
from fastapi import APIRouter, HTTPException, status
from backend.schemas.predict import FQIPredictionRequest, FQIPredictionResponse

logger = logging.getLogger("smartsilage.predict")

router = APIRouter(tags=["ML Prediction"])

# Locate frozen model artifact
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CANDIDATE_PATHS = [
    os.path.join(BASE_DIR, "dataset", "fqi_model.joblib"),
    os.path.join(BASE_DIR, "data", "fqi_model.joblib"),
    os.path.join(BASE_DIR, "models", "fqi_model.joblib")
]

MODEL_PIPELINE = None
MODEL_LOAD_ERROR: Optional[str] = None


def _load_model():
    """Attempts to locate and load the serialized pipeline artifact."""
    global MODEL_PIPELINE, MODEL_LOAD_ERROR
    for path in CANDIDATE_PATHS:
        if os.path.exists(path):
            try:
                MODEL_PIPELINE = joblib.load(path)
                MODEL_LOAD_ERROR = None
                logger.info(f"[SmartSilageAI] Successfully loaded FQI model pipeline from: {path}")
                return MODEL_PIPELINE
            except Exception as e:
                MODEL_LOAD_ERROR = str(e)
                logger.warning(f"[SmartSilageAI Warning] Failed to load model from {path}: {e}")

    if MODEL_PIPELINE is None and MODEL_LOAD_ERROR is None:
        MODEL_LOAD_ERROR = "Model artifact file not found on disk."
    return MODEL_PIPELINE


# Initial load attempt on module import
_load_model()


def get_pipeline():
    """Returns the loaded pipeline or raises a 503 Service Unavailable."""
    global MODEL_PIPELINE
    if MODEL_PIPELINE is not None:
        return MODEL_PIPELINE

    # Retry loading in case the file was placed or regenerated after startup
    pipeline = _load_model()
    if pipeline is not None:
        return pipeline

    logger.error(f"[SmartSilageAI Error] FQI model unavailable: {MODEL_LOAD_ERROR}")
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="FQI prediction model is not currently available. Please verify the model artifact is installed on the server."
    )


@router.post(
    "/predict",
    response_model=FQIPredictionResponse,
    summary="Predict Fermentation Quality Index (FQI)",
    description=(
        "Evaluates pre-ensiling forage characteristics and management decisions using the "
        "validated Random Forest regression pipeline. "
        "Input features are dynamically aligned to the active model pipeline."
    )
)
@router.post(
    "/api/predict",
    response_model=FQIPredictionResponse,
    include_in_schema=False
)
def predict_fqi(payload: FQIPredictionRequest) -> FQIPredictionResponse:
    pipeline = get_pipeline()

    # Determine features expected by the active model
    expected_cols = getattr(pipeline, "feature_names_in_", None)
    expected_list = list(expected_cols) if expected_cols is not None else None

    # Step 1: Input conversion and alignment
    try:
        input_df = payload.to_dataframe(expected_features=expected_list)
    except ValueError as ve:
        # User input missing a feature required by the loaded model
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input data: {str(ve)}"
        )
    except Exception as e:
        logger.warning(f"DataFrame conversion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process input parameters. Please verify input formats."
        )

    # Step 2: Model inference
    try:
        raw_pred = pipeline.predict(input_df)[0]
    except Exception as e:
        logger.exception(f"Internal inference error during FQI prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while evaluating the prediction model. Please check the inputs or contact support."
        )

    # Step 3: Format output with continuous score and scientific transparency
    formatted_fqi = round(float(raw_pred), 2)
    feature_count = len(expected_list) if expected_list else len(input_df.columns)

    return FQIPredictionResponse(
        predicted_fqi=formatted_fqi,
        model_feature_count=feature_count,
        scientific_disclaimer=(
            f"Research prototype estimate evaluated via {feature_count}-feature Random Forest pipeline. "
            "Not a certified laboratory diagnosis or animal safety guarantee."
        )
    )

