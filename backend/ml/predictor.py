"""
Predictor module for SmartSilageAI (SIH26111)
Executes rapid preliminary quality screening using scientifically grounded dairy science heuristics
or loads a trained scikit-learn model once validated.
Always distinguishes preliminary screening from laboratory proximate testing.
"""
from typing import Dict, Any, List
from .preprocessing import preprocess_sample_features, create_ml_feature_vector
from .model_loader import load_trained_model, get_model_status


# Scientific benchmark ranges derived from ICAR-NDRI & dairy extension standards
REFERENCE_BENCHMARKS = {
    "Corn Silage": {
        "ph": {"optimal_min": 3.7, "optimal_max": 4.2, "critical_max": 4.8},
        "moisture": {"optimal_min": 60.0, "optimal_max": 70.0, "critical_min": 50.0, "critical_max": 75.0},
        "temp_threshold": 32.0,
        "critical_temp": 40.0,
        "target_cp": 8.0,
        "target_ndf": 45.0,
    },
    "Sorghum Silage": {
        "ph": {"optimal_min": 3.8, "optimal_max": 4.3, "critical_max": 5.0},
        "moisture": {"optimal_min": 62.0, "optimal_max": 72.0, "critical_min": 52.0, "critical_max": 76.0},
        "temp_threshold": 32.0,
        "critical_temp": 40.0,
        "target_cp": 7.5,
        "target_ndf": 52.0,
    },
    "Mixed Grass Silage": {
        "ph": {"optimal_min": 4.2, "optimal_max": 4.8, "critical_max": 5.4},
        "moisture": {"optimal_min": 60.0, "optimal_max": 70.0, "critical_min": 50.0, "critical_max": 76.0},
        "temp_threshold": 32.0,
        "critical_temp": 40.0,
        "target_cp": 9.0,
        "target_ndf": 55.0,
    },
    "Default": {
        "ph": {"optimal_min": 3.8, "optimal_max": 4.4, "critical_max": 5.0},
        "moisture": {"optimal_min": 60.0, "optimal_max": 70.0, "critical_min": 50.0, "critical_max": 75.0},
        "temp_threshold": 32.0,
        "critical_temp": 40.0,
        "target_cp": 8.0,
        "target_ndf": 50.0,
    }
}


def evaluate_heuristics(sample: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates feed/silage measurements against standard ICAR/NDRI dairy benchmarks.
    Produces an explainable breakdown of each physical parameter without fake predictions.
    """
    stype = sample.get("sample_type", "Corn Silage")
    bm = REFERENCE_BENCHMARKS.get(stype, REFERENCE_BENCHMARKS["Default"])
    
    indicators: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    concerning_count = 0
    severe_count = 0
    
    # 1. pH Evaluation
    ph = sample.get("ph")
    if ph is not None:
        opt_min = bm["ph"]["optimal_min"]
        opt_max = bm["ph"]["optimal_max"]
        crit_max = bm["ph"]["critical_max"]
        
        if opt_min <= ph <= opt_max:
            status = "Optimal"
            explanation = f"pH {ph} is within the ideal lactic acid fermentation zone ({opt_min} - {opt_max}). Inhibits undesirable bacteria."
            severity = "success"
        elif ph < opt_min:
            status = "Low pH"
            explanation = f"pH {ph} is unusually acidic (< {opt_min}). May reduce palatability or indicate excessive acid accumulation."
            severity = "warning"
            concerning_count += 1
            recommendations.append("Monitor feed intake. Consider blending with dry hay or buffer if cattle show mild acidosis signs.")
        elif ph <= crit_max:
            status = "Borderline Elevated"
            explanation = f"pH {ph} is higher than ideal ({opt_min} - {opt_max}). Fermentation may be incomplete or air was trapped during packing."
            severity = "warning"
            concerning_count += 1
            recommendations.append("Inspect pit/bunker packing density. Ensure plastic covers are weighted and airtight.")
        else:
            status = "Critically High"
            explanation = f"pH {ph} exceeds critical safety benchmark ({crit_max}). High risk of secondary clostridial breakdown, protein degradation, and butyric acid formation."
            severity = "danger"
            severe_count += 1
            recommendations.append("CRITICAL: Elevated pH poses clostridial risk. Check for rancid smell. Avoid feeding to high-yielding or pregnant animals.")
        
        indicators.append({
            "parameter": "pH (Acidity)",
            "measured_value": f"{ph:.1f}",
            "reference_target": f"{opt_min} - {opt_max}",
            "status": status,
            "severity": severity,
            "explanation": explanation,
            "category": "Field Measurement"
        })
    else:
        indicators.append({
            "parameter": "pH (Acidity)",
            "measured_value": "Not provided",
            "reference_target": f"{bm['ph']['optimal_min']} - {bm['ph']['optimal_max']}",
            "status": "Optional Missing",
            "severity": "neutral",
            "explanation": "pH is a primary field fermentation check. Portable pH strips or digital pocket meters cost under Rs. 300.",
            "category": "Field Measurement"
        })

    # 2. Moisture / Dry Matter Evaluation
    moisture = sample.get("moisture")
    if moisture is not None:
        opt_min = bm["moisture"]["optimal_min"]
        opt_max = bm["moisture"]["optimal_max"]
        crit_min = bm["moisture"]["critical_min"]
        crit_max = bm["moisture"]["critical_max"]
        
        if opt_min <= moisture <= opt_max:
            status = "Optimal"
            explanation = f"Moisture {moisture:.1f}% provides ideal anaerobic consolidation without excessive seepage."
            severity = "success"
        elif moisture > crit_max:
            status = "Excessively Wet"
            explanation = f"Moisture {moisture:.1f}% (> {crit_max}%) causes effluent seepage, leaching soluble nutrients and predisposing to clostridial spoilage."
            severity = "danger"
            severe_count += 1
            recommendations.append("High moisture silage leads to nutrient loss through seepage. Check runoff drainage.")
        elif moisture > opt_max:
            status = "Slightly Wet"
            explanation = f"Moisture {moisture:.1f}% is somewhat elevated ({opt_min} - {opt_max}% target)."
            severity = "warning"
            concerning_count += 1
        elif moisture < crit_min:
            status = "Excessively Dry"
            explanation = f"Moisture {moisture:.1f}% (< {crit_min}%) makes air expulsion difficult during packing, increasing trapped oxygen."
            severity = "warning"
            concerning_count += 1
            recommendations.append("Dry crop traps air in the silo. Ensure rapid packing and heavy rolling to prevent mold pockets.")
        else:
            status = "Acceptable Dry"
            explanation = f"Moisture {moisture:.1f}% is slightly below ideal range."
            severity = "warning"
        
        indicators.append({
            "parameter": "Moisture / Dry Matter",
            "measured_value": f"{moisture:.1f}% (DM: {100 - moisture:.1f}%)",
            "reference_target": f"{opt_min}% - {opt_max}%",
            "status": status,
            "severity": severity,
            "explanation": explanation,
            "category": "Field Measurement"
        })

    # 3. Internal Temperature Evaluation
    temp = sample.get("temperature")
    if temp is not None:
        thresh = bm["temp_threshold"]
        crit_temp = bm["critical_temp"]
        
        if temp <= thresh:
            status = "Normal / Stable"
            explanation = f"Temperature {temp:.1f}°C indicates stable anaerobic storage without active aerobic heating."
            severity = "success"
        elif temp <= crit_temp:
            status = "Mild Heating"
            explanation = f"Temperature {temp:.1f}°C (> {thresh}°C) indicates air penetration (aerobic deterioration). Yeasts and molds are becoming active."
            severity = "warning"
            concerning_count += 1
            recommendations.append("Feed out silage face at least 15-20 cm daily to stay ahead of aerobic heating zone.")
        else:
            status = "Severe Aerobic Heating"
            explanation = f"Temperature {temp:.1f}°C is critically high (> {crit_temp}°C). Significant nutrient burnout, Maillard caramelization, and mold spore growth."
            severity = "danger"
            severe_count += 1
            recommendations.append("CRITICAL: Silage is actively heating. Discard dark, hot outer crust. Do not feed heated/steaming silage.")
        
        indicators.append({
            "parameter": "Internal Temperature",
            "measured_value": f"{temp:.1f}°C",
            "reference_target": f"Ambient (< {thresh}°C)",
            "status": status,
            "severity": severity,
            "explanation": explanation,
            "category": "Field Measurement"
        })

    # 4. Sensory & Visual Observations
    odor = sample.get("visual_odor")
    color = sample.get("visual_color")
    
    if odor:
        if "Pleasant" in odor or "Acidic" in odor or "Fruity" in odor:
            indicators.append({
                "parameter": "Odor / Aroma",
                "measured_value": odor,
                "reference_target": "Pleasant acidic / Clean lactic",
                "status": "Good Fermentation Aroma",
                "severity": "success",
                "explanation": "Desirable lactic acid aroma typical of sound silage preservation.",
                "category": "Sensory Observation"
            })
        elif "Vinegar" in odor or "Acetic" in odor:
            concerning_count += 1
            indicators.append({
                "parameter": "Odor / Aroma",
                "measured_value": odor,
                "reference_target": "Clean lactic",
                "status": "Acetic Aroma",
                "severity": "warning",
                "explanation": "Sharp vinegar smell suggests prolonged heterolactic fermentation.",
                "category": "Sensory Observation"
            })
        elif "Rancid" in odor or "Butyric" in odor or "Foul" in odor:
            severe_count += 1
            recommendations.append("Strong rancid/butyric odor signifies protein breakdown. Cattle may refuse this feed.")
            indicators.append({
                "parameter": "Odor / Aroma",
                "measured_value": odor,
                "reference_target": "Clean lactic",
                "status": "Rancid / Butyric Odor",
                "severity": "danger",
                "explanation": "Butyric acid aroma caused by clostridia bacteria. Highly unpalatable and risk of ketosis.",
                "category": "Sensory Observation"
            })
        elif "Musty" in odor or "Mold" in odor:
            severe_count += 1
            recommendations.append("Musty/mold odor indicates fungal activity. Inspect visually for white/green mycelium.")
            indicators.append({
                "parameter": "Odor / Aroma",
                "measured_value": odor,
                "reference_target": "Clean lactic",
                "status": "Musty / Moldy Odor",
                "severity": "danger",
                "explanation": "Fungal growth detected. Potential risk of mycotoxins (Aflatoxin, Zearalenone, DON).",
                "category": "Sensory Observation"
            })

    if color:
        if "Mold" in color or "White" in color:
            severe_count += 1
            recommendations.append("Discard moldy sections. Never mix moldy feed into Total Mixed Ration (TMR).")
            indicators.append({
                "parameter": "Visual Appearance",
                "measured_value": color,
                "reference_target": "Olive green to golden brown",
                "status": "Fungal Mycelium / Mold Signs",
                "severity": "danger",
                "explanation": "Visible mold patches present. Spores cause respiratory irritation and toxic mycotoxins.",
                "category": "Sensory Observation"
            })
        elif "Dark Brown" in color or "Black" in color or "Burnt" in color:
            concerning_count += 1
            recommendations.append("Dark color indicates heat-damage (Maillard reaction). Protein digestibility is significantly reduced.")
            indicators.append({
                "parameter": "Visual Appearance",
                "measured_value": color,
                "reference_target": "Olive green to golden brown",
                "status": "Heat Damaged / Caramelized",
                "severity": "warning",
                "explanation": "Excessive heating binds proteins to fibers, lowering usable nutritional value.",
                "category": "Sensory Observation"
            })

    # 5. Optional Laboratory Parameters Check (CP, NDF, ADF, Ash)
    cp = sample.get("crude_protein")
    ndf = sample.get("ndf")
    adf = sample.get("adf")
    ash = sample.get("ash")
    
    lab_count = sum(1 for v in [cp, ndf, adf, ash] if v is not None)
    if lab_count > 0:
        if cp is not None:
            target_cp = bm.get("target_cp", 8.0)
            status_cp = "Adequate" if cp >= target_cp else "Below Target"
            sev_cp = "success" if cp >= target_cp else "warning"
            indicators.append({
                "parameter": "Crude Protein (% CP)",
                "measured_value": f"{cp:.1f}%",
                "reference_target": f"≥ {target_cp:.1f}%",
                "status": status_cp,
                "severity": sev_cp,
                "explanation": "Laboratory proximate measure of total nitrogen content (N x 6.25).",
                "category": "Laboratory Assay"
            })
        if ndf is not None:
            indicators.append({
                "parameter": "Neutral Detergent Fiber (% NDF)",
                "measured_value": f"{ndf:.1f}%",
                "reference_target": "40% - 50%",
                "status": "Normal" if ndf <= 52.0 else "High Fiber / Low Intake",
                "severity": "success" if ndf <= 52.0 else "warning",
                "explanation": "Laboratory measure of total plant cell wall. High NDF restricts rumen gut-fill.",
                "category": "Laboratory Assay"
            })

    # Overall Field Scoring Index (Flieg-inspired 0-100 scale)
    base_score = 90.0
    base_score -= (severe_count * 25.0)
    base_score -= (concerning_count * 12.0)
    final_score = max(15.0, min(95.0, round(base_score, 1)))

    # Determine Preliminary Status
    if severe_count > 0:
        preliminary_tier = "High Spoilage Risk Detected"
        lab_needed = True
    elif concerning_count > 0:
        preliminary_tier = "Caution - Requires Attention"
        lab_needed = True
    else:
        preliminary_tier = "Acceptable Preliminary Range"
        lab_needed = False

    # Default farmer recommendations if clean
    if not recommendations:
        recommendations.append("Continue current silage feed-out rate (minimum 15-20 cm face removal daily).")
        recommendations.append("Keep silo edges covered and tightly sealed to prevent secondary aerobic heating.")
        recommendations.append("For high-yield milch herds (>15L/day), periodic laboratory proximate testing is recommended once a month.")

    if lab_needed:
        recommendations.append("RECOMMENDED ACTION: Submit a composite 500g sample to your district veterinary diagnostic lab or dairy cooperative testing facility for comprehensive wet chemistry / mycotoxin screening.")

    return {
        "quality_category": "Prototype — AI model pending validation",
        "preliminary_field_tier": preliminary_tier,
        "quality_score": final_score,
        "confidence": "Field Reference Screening (Pre-ML Validation)",
        "model_version": "Heuristic-v1.0 (ML Model Pending)",
        "indicators": indicators,
        "recommendations": recommendations,
        "lab_recommended": lab_needed,
        "is_prototype": True,
        "dataset_status": "Pending",
        "model_status": "Not yet trained"
    }


def predict_quality(sample_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Primary prediction entrypoint.
    Inspects model availability; if absent, runs transparent dairy heuristic engine.
    """
    model = load_trained_model()
    processed = preprocess_sample_features(sample_data)
    
    if model is not None:
        try:
            # If a trained model is provided in the future, pass feature vector
            feature_vec = create_ml_feature_vector(processed)
            prediction = model.predict(feature_vec)[0]
            # Augment with explainable breakdown
            result = evaluate_heuristics(processed)
            result["quality_category"] = str(prediction)
            result["confidence"] = "Supervised ML Prediction (Active Model)"
            result["model_version"] = "v1.0-Validated"
            result["is_prototype"] = False
            return result
        except Exception:
            # Fallback to heuristic
            pass
            
    # Default: Transparent Prototype Screening Mode
    return evaluate_heuristics(processed)
