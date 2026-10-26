"""
Comprehensive Verification Suite for SmartSilageAI Farmer-Friendly UX Upgrade (SIH26111)
Tests:
1. Health and System Transparency
2. Farmer Mode Guidance (No lab report required)
3. Farmer Mode Warning Signs Detection (Mould, Foul Odor, Heating)
4. Farmer Mode Database Persistence (Sample & Assessment creation)
5. ML Model Missing Inputs Validation (Never fabricates FQI predictions)
6. ML Model Invalid Inputs Validation (Strict schema validation)
7. ML Model Valid 11-Feature Inference (Continuous predicted FQI)
8. Sample History and Dashboard Integration
9. Existing Admin Pipeline Verification
10. Bilingual (Tamil/English) Localization Consistency
"""

import sys
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.farmer_guidance_service import evaluate_farmer_mode


def run_comprehensive_tests():
    print("=" * 70)
    print("SmartSilageAI (SIH26111) — Farmer UX & ML Model Verification Suite")
    print("=" * 70)

    client = TestClient(app)
    passed = 0
    failed = 0

    def record_pass(test_id, name, detail=""):
        nonlocal passed
        passed += 1
        print(f"[PASS] [{test_id}] {name} {detail}")

    def record_fail(test_id, name, error):
        nonlocal failed
        failed += 1
        print(f"[FAIL] [{test_id}] {name}: {error}")

    # TEST 1: Health Check
    try:
        r = client.get('/health')
        assert r.status_code == 200, f"Status code {r.status_code}"
        record_pass("1/10", "System Health Check", "— Service Healthy")
    except Exception as e:
        record_fail("1/10", "System Health Check", str(e))

    # TEST 2: Farmer Mode Without Lab Report (Clean Sample)
    try:
        payload = {
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
            "save_sample": False
        }
        r = client.post('/api/assessment/farmer-guidance', json=payload)
        assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
        data = r.json()
        assert data["mode"] == "farmer_guided"
        assert data["is_ml_prediction"] is False
        assert "disclaimer_en" in data
        assert "disclaimer_ta" in data
        assert len(data["guidance_en"]) >= 3
        assert len(data["guidance_ta"]) >= 3
        assert "NOT an ML-generated FQI prediction" in data["disclaimer_en"]
        assert "கண்ணுக்குத் தெரியாத பூஞ்சை நச்சுகள்" in data["disclaimer_ta"]
        record_pass("2/10", "Farmer Mode (No Lab Report Required)", "— Clean sensory guidance generated without fake FQI")
    except Exception as e:
        record_fail("2/10", "Farmer Mode (No Lab Report Required)", str(e))

    # TEST 3: Farmer Mode Warning Signs Detection (Spoiled, Mouldy, Heated)
    try:
        spoiled_payload = {
            "crop": "Corn / Maize",
            "harvest_timing": "Late harvest (hard dry grain, dry brown stalks)",
            "sealing_delay": "Delayed overnight / next day (>20 hours delay)",
            "storage_method": "Silage Pit / Bunker Silo",
            "inoculant_used": "No inoculant used / None added",
            "visible_mould": "Extensive mould / deep pockets (green, black, or pink patches)",
            "silage_color": "Dark brown / caramelized (sweet tobacco/burnt bread smell)",
            "silage_odor": "Foul, rotting, rancid butter / pungent ammonia smell",
            "temperature_feeling": "Hot or steaming (severe aerobic heating)",
            "lab_report_available": False,
            "save_sample": False
        }
        r = client.post('/api/assessment/farmer-guidance', json=spoiled_payload)
        assert r.status_code == 200, f"Status {r.status_code}"
        data = r.json()
        assert data["lab_recommended"] is True
        severities = [s["severity"] for s in data["warning_signs"]]
        assert "danger" in severities, "Danger signs not detected"
        assert len(data["warning_signs"]) >= 4
        # Verify both English and Tamil warning signs exist
        for s in data["warning_signs"]:
            assert "category" in s and "category_ta" in s
            assert "title" in s and "title_ta" in s
            assert "description" in s and "description_ta" in s
        record_pass("3/10", "Warning Signs & Risk Detection", f"— Identified {len(data['warning_signs'])} risk indicators (Mould, Odour, Heating, Delay)")
    except Exception as e:
        record_fail("3/10", "Warning Signs & Risk Detection", str(e))

    # TEST 4: Farmer Mode Database Persistence (Save to History)
    try:
        save_payload = {
            "crop": "Sorghum / Jowar",
            "harvest_timing": "Recommended mid-milk line (50% grain dent, optimal moisture)",
            "sealing_delay": "Sealed quickly (within 0–4 hours of chopping)",
            "storage_method": "Silage Bags / Tube Bags",
            "inoculant_used": "Yes, biological bacterial culture (homo/heterofermentative)",
            "visible_mould": "No mould visible / Clean forage",
            "silage_color": "Healthy olive green to golden/light brown",
            "silage_odor": "Pleasant, mildly acidic / fruity / yogurt-like (clean lactic)",
            "temperature_feeling": "Cool or normal ambient temperature",
            "lab_report_available": False,
            "ph": 3.9,
            "moisture": 66.0,
            "temperature": 26.0,
            "notes": "Automated verification sample for Farmer Mode persistence",
            "save_sample": True
        }
        r = client.post('/api/assessment/farmer-guidance', json=save_payload)
        assert r.status_code == 200
        data = r.json()
        assert data["sample_id"] is not None
        assert data["db_id"] is not None
        sample_code = data["sample_id"]
        sample_id = data["db_id"]

        # Fetch sample details from DB via /api/samples/{id}
        r_fetch = client.get(f'/api/samples/{sample_id}')
        assert r_fetch.status_code == 200
        sample_detail = r_fetch.json()
        assert sample_detail["sample_id"] == sample_code
        assert sample_detail["sample_type"] == "Sorghum / Jowar"
        assert sample_detail["ph"] == 3.9
        record_pass("4/10", "Farmer Mode Database Persistence", f"— Saved sample {sample_code} (DB ID: {sample_id})")
    except Exception as e:
        record_fail("4/10", "Farmer Mode Database Persistence", str(e))

    # TEST 5: ML Prediction — Missing Inputs Never Fabricate Predictions
    try:
        # Request missing 'dm.f' and 'cp.f'
        incomplete_payload = {
            "ash.f": 3.8,
            "wsc.f": 8.5,
            "starch.f": 30.2,
            "method": "bags",
            "inhoculant": "c",
            "dose": "none",
            "delay": "D0",
            "fao.class": "la",
            "maturity": "mh"
        }
        r = client.post('/predict', json=incomplete_payload)
        # Must return 422 Unprocessable Entity, NEVER fabricate an FQI
        assert r.status_code == 422, f"Expected 422, got {r.status_code}: {r.text}"
        record_pass("5/10", "ML Missing Inputs Protection", "— HTTP 422 returned; no fabricated prediction generated")
    except Exception as e:
        record_fail("5/10", "ML Missing Inputs Protection", str(e))

    # TEST 6: ML Prediction — Invalid Data Types Rejected
    try:
        invalid_payload = {
            "dm.f": "not-a-number",
            "cp.f": 8.2,
            "ash.f": 3.8,
            "wsc.f": 8.5,
            "starch.f": 30.2,
            "method": "bags",
            "inhoculant": "c",
            "dose": "none",
            "delay": "D0",
            "fao.class": "la",
            "maturity": "mh"
        }
        r = client.post('/predict', json=invalid_payload)
        assert r.status_code == 422, f"Expected 422, got {r.status_code}"
        record_pass("6/10", "ML Invalid Data Type Validation", "— Non-numeric input rejected by schema")
    except Exception as e:
        record_fail("6/10", "ML Invalid Data Type Validation", str(e))

    # TEST 7: ML Prediction — Valid 11-Feature Submission
    try:
        valid_ml_payload = {
            "dm.f": 34.5,
            "cp.f": 8.2,
            "ash.f": 3.8,
            "wsc.f": 8.5,
            "starch.f": 30.2,
            "method": "bags",
            "inhoculant": "c",
            "dose": "none",
            "delay": "D0",
            "fao.class": "la",
            "maturity": "mh"
        }
        r = client.post('/predict', json=valid_ml_payload)
        assert r.status_code == 200, f"Prediction error: {r.text}"
        res = r.json()
        assert "predicted_fqi" in res
        score = res["predicted_fqi"]
        assert isinstance(score, (int, float))
        assert 10.0 <= score <= 90.0
        # Also test via /api/predict alias
        r_alias = client.post('/api/predict', json=valid_ml_payload)
        assert r_alias.status_code == 200
        record_pass("7/10", "Valid ML 11-Feature Prediction", f"— Predicted FQI: {score} (Continuous score, no invented bins)")
    except Exception as e:
        record_fail("7/10", "Valid ML 11-Feature Prediction", str(e))

    # TEST 8: Existing Auth & Sample Submission Preserved
    try:
        r_login = client.post('/api/login', json={'mobile': '9876543210', 'password': 'farmer123'})
        assert r_login.status_code == 200
        token = r_login.json()["access_token"]

        sample_form = {
            'sample_type': 'Corn Silage',
            'ph': '3.9',
            'moisture': '65.0',
            'temperature': '26.0',
            'crude_protein': '8.4',
            'ndf': '44.0',
            'adf': '26.5',
            'ash': '4.8',
            'visual_odor': 'Pleasant / Fruity Acidic',
            'visual_color': 'Olive Green / Light Brown',
            'notes': 'Verified integration test sample'
        }
        r_create = client.post('/api/samples', data=sample_form, headers={'Authorization': f'Bearer {token}'})
        assert r_create.status_code == 201
        new_sample_id = r_create.json()["id"]

        r_dash = client.get('/api/dashboard', headers={'Authorization': f'Bearer {token}'})
        assert r_dash.status_code == 200
        dash_data = r_dash.json()
        assert dash_data["total_samples"] >= 1
        record_pass("8/10", "Auth, Sample Creation & Dashboard Integration", f"— Total samples: {dash_data['total_samples']}")
    except Exception as e:
        record_fail("8/10", "Auth, Sample Creation & Dashboard Integration", str(e))

    # TEST 9: Admin Pipeline & Model Status Transparency
    try:
        r_admin = client.get('/api/admin/status')
        assert r_admin.status_code == 200
        admin_data = r_admin.json()
        assert admin_data["dataset_status"] == "Pending (No fabricated/synthetic data used)"
        assert admin_data["model_status"] == "Not yet trained"

        r_pipe = client.post('/api/admin/test-pipeline')
        assert r_pipe.status_code == 200
        assert r_pipe.json()["status"] == "Pipeline Operational"
        record_pass("9/10", "Admin Diagnostics & Pipeline Dry-Run", "— Verified status & transparency")
    except Exception as e:
        record_fail("9/10", "Admin Diagnostics & Pipeline Dry-Run", str(e))

    # TEST 10: Bilingual (English / Tamil) Localization Consistency
    try:
        import os
        import json
        i18n_path = os.path.join(os.path.dirname(__file__), "frontend", "js", "i18n.js")
        assert os.path.exists(i18n_path), "i18n.js not found"
        with open(i18n_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "en: {" in content and "ta: {" in content
        assert "மக்காச்சோளம்" in content  # Tamil Corn
        assert "விவசாயி முறை" in content  # Tamil Farmer Mode
        assert "அறிவியல் FQI" in content   # Tamil Scientific Mode
        assert "பூஞ்சை நச்சு" in content   # Tamil Mycotoxin
        record_pass("10/10", "Bilingual Localization (Tamil/English)", "— Authentic Tamil agricultural terms verified")
    except Exception as e:
        record_fail("10/10", "Bilingual Localization (Tamil/English)", str(e))

    print("\n" + "=" * 70)
    print(f"TEST RESULTS SUMMARY: {passed} PASSED / {failed} FAILED (Total: {passed + failed})")
    print("=" * 70)
    return failed == 0


if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
