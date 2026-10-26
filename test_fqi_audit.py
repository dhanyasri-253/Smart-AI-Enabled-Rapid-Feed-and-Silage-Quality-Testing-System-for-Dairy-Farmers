"""
SmartSilageAI (SIH26111) — FQI Prediction Integration Audit Test Suite
Verifies:
1. Schema validation for missing inputs (HTTP 422)
2. Schema validation for invalid data types (HTTP 422)
3. Schema validation for out-of-boundary values (HTTP 422)
4. Strict leakage prevention: post-ensiling features (pH, lactic acid) and ref.trial forbidden (HTTP 422)
5. Valid 11-feature submission produces continuous FQI and disclaimer (HTTP 200)
6. Valid 14-feature submission with approved fiber features accepted and aligned (HTTP 200)
7. Both /predict and /api/predict routes function identically
8. DataFrame column names and ordering match active model expectations
9. Missing model artifact produces HTTP 503 without leaking server file paths
10. Farmer Mode provides practical guidance without fabricating FQI
"""

import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas.predict import FQIPredictionRequest
import backend.routers.predict as predict_module


def run_audit_suite():
    print("=" * 70)
    print("SmartSilageAI (SIH26111) — FQI Prediction Integration Audit Suite")
    print("=" * 70)

    client = TestClient(app)
    passed = 0
    failed = 0

    def record_pass(num, title, detail=""):
        nonlocal passed
        passed += 1
        print(f"[PASS] [{num}/10] {title} {detail}")

    def record_fail(num, title, err):
        nonlocal failed
        failed += 1
        print(f"[FAIL] [{num}/10] {title}: {err}")

    # TEST 1: Missing Required Inputs -> HTTP 422
    try:
        payload = {
            "cp.f": 8.2, "ash.f": 3.8, "wsc.f": 8.5, "starch.f": 30.2,
            "method": "bags", "inhoculant": "c", "dose": "none",
            "delay": "D0", "fao.class": "la", "maturity": "mh"
        }  # Missing 'dm.f'
        r = client.post("/predict", json=payload)
        assert r.status_code == 422, f"Expected 422, got {r.status_code}"
        err_detail = r.json().get("detail", [])
        assert any("dm.f" in str(e) or "dm_f" in str(e) for e in err_detail)
        record_pass(1, "Missing Required Input Rejection", "— Correctly rejected missing dm.f with 422")
    except Exception as e:
        record_fail(1, "Missing Required Input Rejection", str(e))

    # TEST 2: Invalid Data Types -> HTTP 422
    try:
        payload = {
            "dm.f": "not-numeric", "cp.f": 8.2, "ash.f": 3.8, "wsc.f": 8.5, "starch.f": 30.2,
            "method": "bags", "inhoculant": "c", "dose": "none",
            "delay": "D0", "fao.class": "la", "maturity": "mh"
        }
        r = client.post("/predict", json=payload)
        assert r.status_code == 422, f"Expected 422, got {r.status_code}"
        record_pass(2, "Invalid Data Type Rejection", "— Correctly rejected non-float value with 422")
    except Exception as e:
        record_fail(2, "Invalid Data Type Rejection", str(e))

    # TEST 3: Out-of-Bounds Values -> HTTP 422
    try:
        payload = {
            "dm.f": -10.0, "cp.f": 8.2, "ash.f": 3.8, "wsc.f": 8.5, "starch.f": 30.2,
            "method": "bags", "inhoculant": "c", "dose": "none",
            "delay": "D0", "fao.class": "la", "maturity": "mh"
        }
        r = client.post("/predict", json=payload)
        assert r.status_code == 422, f"Expected 422, got {r.status_code}"
        record_pass(3, "Out-of-Bounds Physical Value Rejection", "— Negative percentage rejected with 422")
    except Exception as e:
        record_fail(3, "Out-of-Bounds Physical Value Rejection", str(e))

    # TEST 4: Leakage Feature Rejection (Strict extra='forbid') -> HTTP 422
    try:
        leakage_payload = {
            "dm.f": 34.5, "cp.f": 8.2, "ash.f": 3.8, "wsc.f": 8.5, "starch.f": 30.2,
            "method": "bags", "inhoculant": "c", "dose": "none",
            "delay": "D0", "fao.class": "la", "maturity": "mh",
            "pH": 3.8,  # Post-ensiling leakage feature
            "ref.trial": "1"  # Grouping variable
        }
        r = client.post("/predict", json=leakage_payload)
        assert r.status_code == 422, f"Expected 422 for forbidden leakage fields, got {r.status_code}"
        err_text = r.text.lower()
        assert "extra" in err_text or "ph" in err_text or "ref.trial" in err_text
        record_pass(4, "Post-Ensiling Leakage Rejection", "— Forbade pH and ref.trial with 422")
    except Exception as e:
        record_fail(4, "Post-Ensiling Leakage Rejection", str(e))

    # TEST 5: Valid 11-Feature Submission -> HTTP 200
    try:
        valid_11 = {
            "dm.f": 34.5, "cp.f": 8.2, "ash.f": 3.8, "wsc.f": 8.5, "starch.f": 30.2,
            "method": "bags", "inhoculant": "c", "dose": "none",
            "delay": "D0", "fao.class": "la", "maturity": "mh"
        }
        r = client.post("/predict", json=valid_11)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "predicted_fqi" in data
        assert isinstance(data["predicted_fqi"], (int, float))
        assert 10.0 <= data["predicted_fqi"] <= 90.0
        assert data.get("model_feature_count") == 11
        assert "scientific_disclaimer" in data
        record_pass(5, "Valid 11-Feature Inference", f"— Predicted continuous FQI: {data['predicted_fqi']}")
    except Exception as e:
        record_fail(5, "Valid 11-Feature Inference", str(e))

    # TEST 6: Valid 14-Feature Submission -> HTTP 200
    try:
        valid_14 = {
            "dm.f": 34.5, "cp.f": 8.2, "ash.f": 3.8, "wsc.f": 8.5, "starch.f": 30.2,
            "ndf.f": 44.0, "adf.f": 26.5, "lignin.f": 2.4,
            "method": "bags", "inhoculant": "c", "dose": "none",
            "delay": "D0", "fao.class": "la", "maturity": "mh"
        }
        r = client.post("/predict", json=valid_14)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
        data = r.json()
        assert "predicted_fqi" in data
        assert isinstance(data["predicted_fqi"], (int, float))
        record_pass(6, "Valid 14-Feature Input Alignment", f"— Predicted continuous FQI: {data['predicted_fqi']}")
    except Exception as e:
        record_fail(6, "Valid 14-Feature Input Alignment", str(e))

    # TEST 7: Both /predict and /api/predict Routes Return Identical Results
    try:
        payload = {
            "dm.f": 34.5, "cp.f": 8.2, "ash.f": 3.8, "wsc.f": 8.5, "starch.f": 30.2,
            "method": "bags", "inhoculant": "c", "dose": "none",
            "delay": "D0", "fao.class": "la", "maturity": "mh"
        }
        r1 = client.post("/predict", json=payload)
        r2 = client.post("/api/predict", json=payload)
        assert r1.status_code == 200 and r2.status_code == 200
        assert r1.json()["predicted_fqi"] == r2.json()["predicted_fqi"]
        record_pass(7, "Dual Endpoint Consistency (/predict & /api/predict)", f"— Results identical: {r1.json()['predicted_fqi']}")
    except Exception as e:
        record_fail(7, "Dual Endpoint Consistency (/predict & /api/predict)", str(e))

    # TEST 8: DataFrame Column Order & Names Match Model feature_names_in_
    try:
        pipeline = predict_module.get_pipeline()
        expected = list(pipeline.feature_names_in_)
        req = FQIPredictionRequest(**{
            "dm.f": 34.5, "cp.f": 8.2, "ash.f": 3.8, "wsc.f": 8.5, "starch.f": 30.2,
            "ndf.f": 45.0, "adf.f": 27.0, "lignin.f": 2.5,
            "method": "bags", "inhoculant": "c", "dose": "none",
            "delay": "D0", "fao.class": "la", "maturity": "mh"
        })
        df = req.to_dataframe(expected_features=expected)
        assert list(df.columns) == expected, f"Column mismatch: {list(df.columns)} vs {expected}"
        assert len(df.columns) == 11
        record_pass(8, "DataFrame Column Name & Order Verification", f"— Exact match ({len(expected)} columns)")
    except Exception as e:
        record_fail(8, "DataFrame Column Name & Order Verification", str(e))

    # TEST 9: Missing Model Artifact Returns 503 Without Leaking Disk Paths
    try:
        with patch.object(predict_module, "MODEL_PIPELINE", None):
            with patch.object(predict_module, "_load_model", return_value=None):
                r = client.post("/predict", json={
                    "dm.f": 34.5, "cp.f": 8.2, "ash.f": 3.8, "wsc.f": 8.5, "starch.f": 30.2,
                    "method": "bags", "inhoculant": "c", "dose": "none",
                    "delay": "D0", "fao.class": "la", "maturity": "mh"
                })
                assert r.status_code == 503, f"Expected 503, got {r.status_code}"
                detail = r.json().get("detail", "")
                assert "c:\\" not in detail.lower() and "users" not in detail.lower()
                assert "available" in detail.lower()
        record_pass(9, "Safe 503 Service Unavailable on Missing Model", "— Clean message with zero path leakage")
    except Exception as e:
        record_fail(9, "Safe 503 Service Unavailable on Missing Model", str(e))

    # TEST 10: Farmer Mode Operates Honestly Without Fabricating FQI
    try:
        farmer_payload = {
            "crop": "Corn / Maize",
            "harvest_timing": "Recommended mid-milk line (50% grain dent, optimal moisture)",
            "sealing_delay": "Sealed quickly (within 0–4 hours of chopping)",
            "storage_method": "Silage Pit / Bunker Silo",
            "inoculant_used": "No inoculant used / None added",
            "visible_mould": "No mould visible / Clean forage",
            "silage_color": "Healthy olive green to golden/light brown",
            "silage_odor": "Pleasant, mildly acidic / fruity / yogurt-like (clean lactic)",
            "temperature_feeling": "Cool or normal ambient temperature",
            "lab_report_available": False,
            "ph": None,
            "moisture": None,
            "temperature": None,
            "save_sample": False
        }
        r = client.post("/api/assessment/farmer-guidance", json=farmer_payload)
        assert r.status_code == 200
        data = r.json()
        assert data["is_ml_prediction"] is False
        assert "predicted_fqi" not in data  # NEVER fabricates FQI in Farmer Mode
        assert "guidance_en" in data
        assert len(data["guidance_en"]) >= 1
        record_pass(10, "Farmer Mode / Scientific FQI Separation", "— Honest guidance provided with zero fake FQI")
    except Exception as e:
        record_fail(10, "Farmer Mode / Scientific FQI Separation", str(e))

    print("=" * 70)
    print(f"AUDIT TEST RESULTS: {passed} PASSED / {failed} FAILED (Total: 10)")
    print("=" * 70)
    assert failed == 0, f"{failed} audit tests failed!"


if __name__ == "__main__":
    run_audit_suite()
