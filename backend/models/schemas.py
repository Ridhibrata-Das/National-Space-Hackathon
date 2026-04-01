from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class Vector3D(BaseModel):
    x: float
    y: float
    z: float

class StateVector(BaseModel):
    id: str
    r: Vector3D
    v: Vector3D

class SpacecraftState(BaseModel):
    id: str
    r: Vector3D
    v: Vector3D
    fuel_kg: float = 50.0  # INIT_FUEL
    status: str = "NOMINAL"
    last_updated: datetime

class ScheduledBurn(BaseModel):
    burn_id: str
    satelliteId: str
    burnTime: datetime
    delta_v: Vector3D  # ECI frame
    status: str = "PENDING"

class ConjunctionWarning(BaseModel):
    sat_id: str
    debris_id: str
    tca: datetime
    miss_distance_km: float
    probability: float = 0.0
    status: str = "PENDING_APPROVAL" # PENDING_APPROVAL, APPROVED, EXECUTED, IGNORED
    auto_approve: bool = False

class ManeuverApprovalRequest(BaseModel):
    sat_id: str
    deb_id: str
    approve: bool
    automate: Optional[bool] = False

class TelemetryObject(BaseModel):
    id: str
    type: str  # "SATELLITE" or "DEBRIS"
    r: Vector3D
    v: Vector3D

class TelemetryRequest(BaseModel):
    timestamp: datetime
    objects: List[TelemetryObject]

class SimulationStepRequest(BaseModel):
    step_seconds: int

class ManeuverScheduleRequest(BaseModel):
    satelliteId: str
    maneuver_sequence: List[ScheduledBurn]

class VisualizationSnapshot(BaseModel):
    timestamp: datetime
    satellites: List[Dict]
    debris_cloud: List[Tuple]
