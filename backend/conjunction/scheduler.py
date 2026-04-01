import numpy as np
from datetime import datetime, timedelta
from .. import state
from ..physics.maneuver import rtn_to_eci, validate_burn
from ..physics.ground_stations import has_los
from ..models.schemas import ScheduledBurn, Vector3D

def plan_evasion_burn(sat, cdm, sim_time):
    """
    Calculates an evasion burn for a given conjunction.
    Rule of thumb (Block 4E): 5 m/s prograde nudge.
    """
    # 1. 5 m/s prograde (T-axis) nudge = 0.005 km/s
    dv_rtn = np.array([0.0, 0.005, 0.0]) 
    
    r_vec = np.array([sat.r.x, sat.r.y, sat.r.z])
    v_vec = np.array([sat.v.x, sat.v.y, sat.v.z])
    
    # 2. Convert to ECI
    dv_eci = rtn_to_eci(dv_rtn, r_vec, v_vec)
    
    if not validate_burn(dv_eci):
        return None
    
    # 3. Create scheduled burn (Block 4G)
    burn_id = f"EVASION_{sat.id}_{cdm['deb_id']}"
    burn_time = sim_time # Fire immediately if LOS exists (as per Block 4E simplification)
    
    return ScheduledBurn(
        burn_id=burn_id,
        satelliteId=sat.id,
        burnTime=burn_time,
        delta_v=Vector3D(x=dv_eci[0], y=dv_eci[1], z=dv_eci[2])
    )

def process_cdm_warnings():
    """
    Main loop for decision making (Block 4E/Phase 10).
    Only schedules burns for APPROVED or AUTOMATED warnings.
    """
    executed = []
    
    for key, warning in list(state.cdm_warnings.items()):
        # Handle state logic
        if warning.status in ["EXECUTED", "IGNORED"]:
            continue
            
        # Automatic promotion if auto_approve is set
        if warning.auto_approve and warning.status == "PENDING_APPROVAL":
            warning.status = "APPROVED"
            
        if warning.status != "APPROVED":
            continue # Wait for user click in Mission Control
            
        # Proceed with maneuver for APPROVED warnings
        sat = state.satellites.get(warning.sat_id)
        if not sat: continue
        
        # Calculate Burns (Block 4E Rule of Thumb: 5 m/s Prograde)
        # 1. Evasion Burn (ASAP)
        burn_time = datetime.now() + timedelta(seconds=10)
        dv_rtn = np.array([0.0, 0.005, 0.0]) # 5 m/s T-axis (km/s)
        
        r_vec = np.array([sat.r.x, sat.r.y, sat.r.z])
        v_vec = np.array([sat.v.x, sat.v.y, sat.v.z])
        dv_eci = rtn_to_eci(dv_rtn, r_vec, v_vec)
        
        evasion = ScheduledBurn(
            burn_id=f"EVADE_{warning.sat_id}_{warning.debris_id}",
            satelliteId=warning.sat_id,
            burnTime=burn_time,
            delta_v=Vector3D(x=dv_eci[0], y=dv_eci[1], z=dv_eci[2])
        )
        
        # 2. Recovery Burn (TCA + 30 mins) - Opposite delta-v to return to orbit
        recovery_time = warning.tca + timedelta(minutes=30)
        dv_eci_rec = rtn_to_eci(-dv_rtn, r_vec, v_vec) 
        
        recovery = ScheduledBurn(
            burn_id=f"RECOVER_{warning.sat_id}",
            satelliteId=warning.sat_id,
            burnTime=recovery_time,
            delta_v=Vector3D(x=dv_eci_rec[0], y=dv_eci_rec[1], z=dv_eci_rec[2])
        )
        
        state.scheduled_maneuvers.extend([evasion, recovery])
        warning.status = "EXECUTED"
        executed.append(evasion.burn_id)
        
    return executed
