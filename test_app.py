import sys
from fastapi.testclient import TestClient
from backend.main import app

def run_tests():
    print("Starting SmartSilageAI Automated Verification Suite...")
    client = TestClient(app)

    # 1. Health Endpoint
    r = client.get('/health')
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("[PASS] [1/7] GET /health: Healthy")

    # 2. Admin Status Endpoint
    r = client.get('/api/admin/status')
    assert r.status_code == 200, f"Admin status failed: {r.text}"
    data = r.json()
    assert data["dataset_status"] == "Pending (No fabricated/synthetic data used)"
    assert data["model_status"] == "Not yet trained"
    print(f"[PASS] [2/7] GET /api/admin/status: Verified (Model: {data['model_status']})")

    # 3. Dry-Run ML Pipeline
    r = client.post('/api/admin/test-pipeline')
    assert r.status_code == 200, f"Pipeline test failed: {r.text}"
    pipe_data = r.json()
    assert pipe_data["status"] == "Pipeline Operational"
    print(f"[PASS] [3/7] POST /api/admin/test-pipeline: Operational (Score: {pipe_data['pipeline_output']['quality_score']})")

    # 4. Authentication Login
    r = client.post('/api/login', json={'mobile': '9876543210', 'password': 'farmer123'})
    assert r.status_code == 200, f"Login failed: {r.text}"
    token = r.json()["access_token"]
    print("[PASS] [4/7] POST /api/login: Auth Token Generated for Ramesh Patel")

    # 5. Create New Sample Submission
    sample_payload = {
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
        'notes': 'Verification Test Silage Sample'
    }
    r = client.post('/api/samples', data=sample_payload, headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 201, f"Sample creation failed: {r.text}"
    new_sample = r.json()
    sample_id = new_sample["id"]
    sample_code = new_sample["sample_id"]
    print(f"[PASS] [5/7] POST /api/samples: Created {sample_code} (DB ID: {sample_id})")

    # 6. Fetch Sample Details & Explainable Assessment
    r = client.get(f'/api/samples/{sample_id}')
    assert r.status_code == 200, f"Sample detail failed: {r.text}"
    detail = r.json()
    assert detail["assessment"] is not None
    assessment = detail["assessment"]
    assert assessment["quality_category"] == "Prototype — AI model pending validation"
    breakdown = assessment["parameter_breakdown"]
    assert len(breakdown["indicators"]) >= 4
    print(f"[PASS] [6/7] GET /api/samples/{sample_id}: Validated (Indicators: {len(breakdown['indicators'])}, Tier: {breakdown['preliminary_field_tier']})")

    # 7. Dashboard Metrics
    r = client.get('/api/dashboard', headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200, f"Dashboard failed: {r.text}"
    dash = r.json()
    assert dash["total_samples"] >= 1
    print(f"[PASS] [7/7] GET /api/dashboard: Verified ({dash['total_samples']} samples total, {dash['silage_samples']} silage)")

    print("\n>>> ALL 7 SYSTEM TESTS PASSED SUCCESSFULLY! The SIH26111 prototype is fully functional.")

if __name__ == '__main__':
    run_tests()
