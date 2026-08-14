from fastapi import APIRouter, HTTPException, Depends
from models.schemas import LocalAggregateRequest, ScenarioActivateRequest
from privacy.processor import process_local_data, generate_laplace_noise
from analytics.engine import analyze_area_health
from data.database import get_db_connection, apply_scenario
import math

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "SurakshaNet API"}

@router.get("/scenarios")
def get_scenarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM active_scenario WHERE id = 1")
    active = cursor.fetchone()["name"]
    conn.close()
    
    return {
        "active": active,
        "available": [
            "Normal", 
            "Single Source Spike", 
            "Gastrointestinal Cluster", 
            "Rural Under-Reporting", 
            "Small Group"
        ]
    }

@router.post("/scenarios/activate")
def activate_scenario(req: ScenarioActivateRequest):
    valid_scenarios = [
        "Normal", 
        "Single Source Spike", 
        "Gastrointestinal Cluster", 
        "Rural Under-Reporting", 
        "Small Group"
    ]
    if req.scenario_name not in valid_scenarios:
        raise HTTPException(status_code=400, detail="Invalid scenario name")
    
    try:
        apply_scenario(req.scenario_name)
        return {"status": "success", "active_scenario": req.scenario_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/areas")
def list_areas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM areas")
    areas_list = cursor.fetchall()
    conn.close()

    result = []
    for area in areas_list:
        analysis = analyze_area_health(area["id"])
        if "error" not in analysis:
            result.append({
                "id": area["id"],
                "name": area["name"],
                "status": analysis["status"],
                "risk_score": analysis["risk_score"],
                "population": analysis["population"],
                "confidence": analysis["confidence"]
            })
    return result

@router.get("/areas/{area_id}")
def get_area_details(area_id: str):
    analysis = analyze_area_health(area_id)
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])
    return analysis

@router.get("/areas/{area_id}/signals")
def get_area_signals(area_id: str):
    analysis = analyze_area_health(area_id)
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])
    return {"signals": analysis["signals"]}

@router.get("/areas/{area_id}/risk")
def get_area_risk(area_id: str):
    analysis = analyze_area_health(area_id)
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])
    return {
        "risk_score": analysis["risk_score"],
        "ml_anomaly_score": analysis.get("ml_anomaly_score", 0.0),
        "status": analysis["status"],
        "confidence": analysis["confidence"],
        "reason": analysis["reason"]
    }

@router.get("/areas/{area_id}/explanation")
def get_area_explanation(area_id: str):
    analysis = analyze_area_health(area_id)
    if "error" in analysis:
        raise HTTPException(status_code=404, detail=analysis["error"])
    return {
        "contributions": analysis["contributions"],
        "disclaimer": "Contributions represent this model's relative signal contribution, not medical causation."
    }

@router.get("/areas/{area_id}/privacy")
def get_area_privacy_audit(area_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, timestamp, signal_id, raw_count, noise_added, noised_count, epsilon, sensitivity, status
    FROM privacy_audits
    WHERE area_id = ?
    ORDER BY timestamp DESC
    LIMIT 20
    """, (area_id,))
    rows = cursor.fetchall()
    conn.close()

    audits = []
    for r in rows:
        audits.append({
            "id": r["id"],
            "timestamp": r["timestamp"],
            "signal_id": r["signal_id"],
            "raw_count": r["raw_count"],
            "noise_added": round(r["noise_added"], 2) if r["noise_added"] else None,
            "noised_count": r["noised_count"],
            "epsilon": r["epsilon"],
            "sensitivity": r["sensitivity"],
            "status": r["status"]
        })
    
    return audits

@router.post("/local-data/aggregate")
def aggregate_local_data(req: LocalAggregateRequest):
    # Simulates local processor boundary
    # Raw data list
    raw_list = [rec.model_dump() for rec in req.records]
    
    # Process using processor
    try:
        protected_payload = process_local_data(
            raw_list, 
            req.area_id, 
            req.epsilon, 
            req.sensitivity, 
            req.min_group_size
        )
        return {
            "status": "success",
            "area_id": req.area_id,
            "protected_payload": protected_payload,
            "message": "Aggregated and protected at the local node. Raw patient data scrubbed."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/privacy/protect")
def privacy_protect_demo(value: float, epsilon: float = 1.0, sensitivity: float = 1.0):
    """
    Demonstrates differential privacy math for the UI.
    """
    try:
        noise = generate_laplace_noise(sensitivity, epsilon)
        noised_value = value + noise
        return {
            "original_value": value,
            "noise_added": round(noise, 4),
            "protected_value": round(noised_value, 4),
            "epsilon": epsilon,
            "sensitivity": sensitivity
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
