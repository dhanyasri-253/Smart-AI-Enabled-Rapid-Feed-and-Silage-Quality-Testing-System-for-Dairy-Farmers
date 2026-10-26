"""
Pydantic schemas for FQI prediction endpoint (SIH26111).
Validates raw values for the silage quality features.

Approved 14-feature specification:
- Numerical (8): dm.f, cp.f, ndf.f, adf.f, ash.f, wsc.f, starch.f, lignin.f
- Categorical (6): method, inhoculant, dose, delay, fao.class, maturity

Active saved model artifact (fqi_model.joblib):
- Trained on 11 domain-robust features (excluding ndf.f, adf.f, lignin.f
  due to cross-trial correlation sign inversions documented in research).
- The schema accepts all 14 approved features and dynamically aligns
  columns to the active model pipeline.
- Forbids post-ensiling leakage features (pH, ammonia, dm.loss) and grouping variables (ref.trial).
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class FQIPredictionRequest(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",  # Strictly forbid post-ensiling leakage features and grouping variables
        json_schema_extra={
            "example": {
                "dm.f": 34.5,
                "cp.f": 8.2,
                "ndf.f": 44.0,
                "adf.f": 26.5,
                "ash.f": 3.8,
                "wsc.f": 8.5,
                "starch.f": 30.2,
                "lignin.f": 2.4,
                "method": "bags",
                "inhoculant": "c",
                "dose": "none",
                "delay": "D0",
                "fao.class": "la",
                "maturity": "mh"
            }
        }
    )

    # 5 Core Pre-Ensiling Fresh Nutritional Traits (% DM basis)
    dm_f: float = Field(..., ge=0.0, le=100.0, alias="dm.f", description="Fresh Whole-Crop Dry Matter (%)")
    cp_f: float = Field(..., ge=0.0, le=100.0, alias="cp.f", description="Fresh Crude Protein (% DM)")
    ash_f: float = Field(..., ge=0.0, le=100.0, alias="ash.f", description="Fresh Total Ash (% DM)")
    wsc_f: float = Field(..., ge=0.0, le=100.0, alias="wsc.f", description="Fresh Water-Soluble Carbohydrates (% DM)")
    starch_f: float = Field(..., ge=0.0, le=100.0, alias="starch.f", description="Fresh Starch Content (% DM)")

    # 3 Additional Fiber Traits from the Approved 14-Feature Specification
    ndf_f: Optional[float] = Field(default=None, ge=0.0, le=100.0, alias="ndf.f", description="Fresh Neutral Detergent Fiber (% DM)")
    adf_f: Optional[float] = Field(default=None, ge=0.0, le=100.0, alias="adf.f", description="Fresh Acid Detergent Fiber (% DM)")
    lignin_f: Optional[float] = Field(default=None, ge=0.0, le=100.0, alias="lignin.f", description="Fresh Acid Detergent Lignin (% DM)")

    # 6 Harvest & Agronomic Management Decisions
    method: str = Field(..., min_length=1, description="Silo containment type (e.g. 'bags', 'buckets')")
    inhoculant: str = Field(..., min_length=1, description="Biological additive applied (e.g. 'c', 'he', 'ho')")
    dose: str = Field(..., min_length=1, description="Inoculant application dosage (e.g. 'none', 's', 'h', 'd', 'Unknown')")
    delay: str = Field(..., min_length=1, description="Chopping-to-sealing delay (e.g. 'D0', 'D6', 'D20')")
    fao_class: str = Field(..., min_length=1, alias="fao.class", description="FAO crop maturity class (e.g. 'ea', 'la', 'Unknown')")
    maturity: str = Field(..., min_length=1, description="Kernel milk-line stage (e.g. 'eh', 'mh', 'lh', 'vlh', 'Unknown')")

    def to_dataframe(self, expected_features: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Converts validated request into a DataFrame preserving exact feature names.
        If expected_features is provided (e.g. from pipeline.feature_names_in_),
        validates that all expected features are present and aligns the DataFrame
        columns to the exact order expected by the model.
        """
        row: Dict[str, Any] = {
            "dm.f": float(self.dm_f),
            "cp.f": float(self.cp_f),
            "ash.f": float(self.ash_f),
            "wsc.f": float(self.wsc_f),
            "starch.f": float(self.starch_f),
            "method": str(self.method).strip(),
            "inhoculant": str(self.inhoculant).strip(),
            "dose": str(self.dose).strip(),
            "delay": str(self.delay).strip(),
            "fao.class": str(self.fao_class).strip(),
            "maturity": str(self.maturity).strip(),
        }
        if self.ndf_f is not None:
            row["ndf.f"] = float(self.ndf_f)
        if self.adf_f is not None:
            row["adf.f"] = float(self.adf_f)
        if self.lignin_f is not None:
            row["lignin.f"] = float(self.lignin_f)

        if expected_features:
            missing = [f for f in expected_features if f not in row or row[f] is None]
            if missing:
                raise ValueError(f"Missing required model features: {missing}")
            # Align columns strictly to expected feature list and order
            ordered_data = {col: [row[col]] for col in expected_features}
            return pd.DataFrame(ordered_data)

        return pd.DataFrame([row])


class FQIPredictionResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "predicted_fqi": 54.72,
                "model_feature_count": 11,
                "scientific_disclaimer": "Research prototype estimate based on pre-ensiling traits; not a certified laboratory diagnosis."
            }
        }
    )

    predicted_fqi: float = Field(..., description="Predicted continuous Fermentation Quality Index (FQI)")
    model_feature_count: Optional[int] = Field(default=None, description="Number of features evaluated by the active model")
    scientific_disclaimer: Optional[str] = Field(
        default="Research prototype estimate based on pre-ensiling traits; not a certified laboratory diagnosis.",
        description="Scientific limitations and validation notice"
    )
