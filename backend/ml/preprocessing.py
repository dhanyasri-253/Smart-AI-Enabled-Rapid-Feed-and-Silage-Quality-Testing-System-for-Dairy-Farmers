"""
Preprocessing module for SmartSilageAI (SIH26111)
Validates physical boundaries, formats farmer inputs, and prepares feature vectors for ML/heuristic inference.
"""
from typing import Dict, Any, Tuple, Optional
import numpy as np


# Standard physical plausibility limits
BOUNDS = {
    "ph": (2.5, 12.0, "pH"),
    "moisture": (10.0, 95.0, "% Moisture"),
    "temperature": (0.0, 75.0, "°C Temperature"),
    "crude_protein": (1.0, 45.0, "% Crude Protein"),
    "ndf": (10.0, 90.0, "% NDF"),
    "adf": (5.0, 75.0, "% ADF"),
    "ash": (0.5, 30.0, "% Ash"),
}


def validate_feature_bounds(sample_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validates that numerical values entered by the farmer fall within physically possible bounds.
    Returns (is_valid, error_message).
    """
    for key, (min_val, max_val, label) in BOUNDS.items():
        val = sample_data.get(key)
        if val is not None:
            try:
                f_val = float(val)
                if f_val < min_val or f_val > max_val:
                    return False, f"{label} value ({f_val}) is outside plausible physical range ({min_val} to {max_val}). Please verify measurement."
            except (ValueError, TypeError):
                return False, f"Invalid numerical value for {label}."
    return True, None


def preprocess_sample_features(sample_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cleans and structures input features.
    Retains missing flags so predictions distinguish between field observations and laboratory assays.
    """
    cleaned = {
        "sample_type": str(sample_data.get("sample_type", "Corn Silage")),
        "ph": float(sample_data["ph"]) if sample_data.get("ph") is not None else None,
        "moisture": float(sample_data["moisture"]) if sample_data.get("moisture") is not None else None,
        "temperature": float(sample_data["temperature"]) if sample_data.get("temperature") is not None else None,
        "crude_protein": float(sample_data["crude_protein"]) if sample_data.get("crude_protein") is not None else None,
        "ndf": float(sample_data["ndf"]) if sample_data.get("ndf") is not None else None,
        "adf": float(sample_data["adf"]) if sample_data.get("adf") is not None else None,
        "ash": float(sample_data["ash"]) if sample_data.get("ash") is not None else None,
        "visual_odor": sample_data.get("visual_odor"),
        "visual_color": sample_data.get("visual_color"),
    }
    
    # Calculate Dry Matter % if moisture is present (DM = 100 - Moisture)
    if cleaned["moisture"] is not None:
        cleaned["dry_matter"] = round(100.0 - cleaned["moisture"], 2)
    else:
        cleaned["dry_matter"] = None

    return cleaned


def create_ml_feature_vector(processed: Dict[str, Any], default_imputation: bool = True) -> np.ndarray:
    """
    Prepares a normalized feature array compatible with standard scikit-learn models.
    Features: [ph, moisture, temperature, crude_protein, ndf, adf, ash]
    """
    # Fallback medians from dairy extension reference data for missing optional laboratory features
    defaults = {
        "ph": 4.2,
        "moisture": 65.0,
        "temperature": 25.0,
        "crude_protein": 8.0,
        "ndf": 45.0,
        "adf": 28.0,
        "ash": 5.0,
    }
    
    vec = [
        processed.get("ph") if processed.get("ph") is not None else (defaults["ph"] if default_imputation else 0.0),
        processed.get("moisture") if processed.get("moisture") is not None else (defaults["moisture"] if default_imputation else 0.0),
        processed.get("temperature") if processed.get("temperature") is not None else (defaults["temperature"] if default_imputation else 0.0),
        processed.get("crude_protein") if processed.get("crude_protein") is not None else (defaults["crude_protein"] if default_imputation else 0.0),
        processed.get("ndf") if processed.get("ndf") is not None else (defaults["ndf"] if default_imputation else 0.0),
        processed.get("adf") if processed.get("adf") is not None else (defaults["adf"] if default_imputation else 0.0),
        processed.get("ash") if processed.get("ash") is not None else (defaults["ash"] if default_imputation else 0.0),
    ]
    return np.array([vec], dtype=np.float32)
