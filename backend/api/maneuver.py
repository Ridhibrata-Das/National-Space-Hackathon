from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from ..models.schemas import ManeuverScheduleRequest, ManeuverApprovalRequest
from .. import state

router = APIRouter()

@router.post("/maneuver/approve")
async def approve_maneuver(data: ManeuverApprovalRequest):
    """Update approval status for a conjunction warning."""
    key = f"{data.sat_id}_{data.deb_id}"
    warning = state.cdm_warnings.get(key)
    if not warning:
        raise HTTPException(status_code=404, detail="Conjunction warning not found")
    
    if data.approve:
        warning.status = "APPROVED"
    else:
        warning.status = "IGNORED"
        
    if data.automate:
        warning.auto_approve = True
        
    return {"status": "SUCCESS", "new_state": warning.status}

@router.post("/maneuver/schedule")
async def schedule_maneuver(data: ManeuverScheduleRequest):
    """
    Validate LOS + cooldown + fuel. (Block 4G)
    If valid, add to state.scheduled_maneuvers.
    """
    sat = state.satellites.get(data.satelliteId)
    if not sat:
        raise HTTPException(status_code=404, detail="Satellite not found")
        
    # 1. Check LOS (Simple check for current time)
    sat_pos = np.array([sat.r.x, sat.r.y, sat.r.z])
    if not has_los(sat_pos, 0): # Using sim offset 0 for now
        raise HTTPException(status_code=400, detail="No Ground Station LOS")
        
    # 2. Check Cooldown/Fuel (To be implemented in detail)
    # For now, just append to schedule
    state.scheduled_maneuvers.extend(data.maneuver_sequence)
    
    return {
        "status": "SCHEDULED",
        "maneuver_count": len(data.maneuver_sequence)
    }
