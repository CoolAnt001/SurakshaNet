import pytest
from fastapi.testclient import TestClient
from main import app
from privacy.processor import generate_laplace_noise, process_local_data
from analytics.engine import calculate_z_score, analyze_area_health
from data.database import apply_scenario, init_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    init_db()

def test_laplace_noise():
    # Test that noise varies, and raises error for epsilon <= 0
    noise1 = generate_laplace_noise(1.0, 1.0)
    noise2 = generate_laplace_noise(1.0, 1.0)
    assert noise1 != noise2
    
    with pytest.raises(ValueError):
        generate_laplace_noise(1.0, -0.5)

def test_small_group_suppression():
    # If raw records count is less than 10, the output must be "SUPPRESSED"
    raw_records = [
        {"patient_id": "P1", "age": 20, "hostel": "A", "symptom": "fever"},
        {"patient_id": "P2", "age": 22, "hostel": "B", "symptom": "fever"}
    ]
    # Epsilon = 1, sensitivity = 1, min_group_size = 5
    # Fever count is 2 (less than 5) -> should suppress
    payload = process_local_data(raw_records, "small_village", epsilon=1.0, sensitivity=1.0, min_group_size=5)
    assert payload["fever"] == "SUPPRESSED"

    # Fever count is 2 (greater than or equal to 2) -> should transmit noised count
    payload2 = process_local_data(raw_records, "small_village", epsilon=1.0, sensitivity=1.0, min_group_size=2)
    assert isinstance(payload2["fever"], float)

def test_z_score_calculation():
    # Fever observed = 22, mean = 12, std = 2
    # Z-score should be (22-12)/2 = 5.0
    z = calculate_z_score(22.0, 12.0, 2.0, "fever")
    assert z == 5.0

    # Under-baseline observed for fever should be 0.0 (positive deviation only)
    z_under = calculate_z_score(5.0, 12.0, 2.0, "fever")
    assert z_under == 0.0

    # pH should be two-sided
    z_ph = calculate_z_score(6.2, 7.2, 0.2, "water_ph")
    assert z_ph == pytest.approx(5.0)

def test_scenario_normal():
    # Activate normal scenario
    response = client.post("/api/scenarios/activate", json={"scenario_name": "Normal"})
    assert response.status_code == 200
    
    # Check CDA Sector 9 details
    details_resp = client.get("/api/areas/cda_sector_9")
    assert details_resp.status_code == 200
    data = details_resp.json()
    assert data["status"] == "NORMAL"
    assert data["risk_score"] < 25.0

def test_scenario_single_source_spike():
    # Activate single source spike
    response = client.post("/api/scenarios/activate", json={"scenario_name": "Single Source Spike"})
    assert response.status_code == 200
    
    # Check details
    data = client.get("/api/areas/cda_sector_9").json()
    # Should flag as VERIFY (due to single signal category spike)
    assert data["status"] == "VERIFY"
    assert "Signal mismatch" in data["reason"]

def test_scenario_gi_cluster():
    # Activate GI cluster
    response = client.post("/api/scenarios/activate", json={"scenario_name": "Gastrointestinal Cluster"})
    assert response.status_code == 200
    
    # Check details
    data = client.get("/api/areas/cda_sector_9").json()
    assert data["status"] == "ELEVATED"
    assert data["risk_score"] > 50.0
    assert "gastrointestinal" in data["contributions"]
    assert "water_contamination" in data["contributions"]

def test_scenario_small_group_suppression():
    response = client.post("/api/scenarios/activate", json={"scenario_name": "Small Group"})
    assert response.status_code == 200
    
    data = client.get("/api/areas/small_village").json()
    assert data["status"] == "SUPPRESSED"
    assert data["risk_score"] == 0.0
    assert "Insufficient group size" in data["reason"]

def test_api_invalid_scenario():
    response = client.post("/api/scenarios/activate", json={"scenario_name": "Unknown Scenario"})
    assert response.status_code == 400
