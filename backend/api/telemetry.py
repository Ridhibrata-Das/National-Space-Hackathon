from fastapi import APIRouter
from ..models.schemas import TelemetryRequest, SpacecraftState, StateVector
from .. import state

router = APIRouter()

@router.post("/telemetry")
async def ingest_telemetry(data: TelemetryRequest):
    """
    Parses JSON -> updates state.satellites or state.debris.
    Must return in under 5ms (Block 4G).
    """
    processed_count = 0
    for obj in data.objects:
        if obj.type == "SATELLITE":
            state.satellites[obj.id] = SpacecraftState(
                id=obj.id,
                r=obj.r,
                v=obj.v,
                last_updated=data.timestamp
            )
        else:
            state.debris[obj.id] = StateVector(
                id=obj.id,
                r=obj.r,
                v=obj.v
            )
        processed_count += 1
    
    return {
        "status": "ACK",
        "processed_count": processed_count,
        "active_cdm_warnings": len(state.cdm_warnings)
    }
