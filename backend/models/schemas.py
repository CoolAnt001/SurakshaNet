from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SymptomRecord(BaseModel):
    patient_id: str = Field(..., description="Unique patient identification code (scrubbed locally)")
    age: int = Field(..., ge=0, le=120, description="Age of the patient")
    hostel: str = Field(..., description="Location of patient residency (scrubbed locally)")
    symptom: str = Field(..., description="Primary reported symptom (fever, cough, diarrhea, etc.)")

class LocalAggregateRequest(BaseModel):
    area_id: str
    records: List[SymptomRecord]
    epsilon: float = Field(1.0, gt=0, description="Differential privacy budget parameter")
    sensitivity: float = Field(1.0, gt=0, description="Sensitivity of counting function")
    min_group_size: int = Field(10, ge=1, description="Minimum population size required to avoid suppression")

class ScenarioActivateRequest(BaseModel):
    scenario_name: str
