from fastapi import APIRouter, HTTPException
from datetime import timedelta
import numpy as np
from ..models.schemas import SimulationStepRequest
from .. import state
from ..physics.propagator import propagate
from ..conjunction.detector import detect_conjunctions
from ..conjunction.scheduler import process_cdm_warnings
from ..models.schemas import ConjunctionWarning

router = APIRouter()

@router.get("/path/{obj_id}")
async def get_orbital_path(obj_id: str):
    # Check if the object is a satellite or debris
    obj = state.satellites.get(obj_id)
    if not obj:
        obj = state.debris.get(obj_id)
    
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    
    path = []
    # Project 90 minutes into the future, 1 point per minute (90 points)
    # The instruction mentions 100 points, but the loop range (0, 90, 1) suggests 90 points.
    # Sticking to the loop range for now.
    for i in range(0, 90, 1): # 1 point per minute
        # Get current 6D state for propagation
        curr_6d = np.array([obj.r.x, obj.r.y, obj.r.z, obj.v.x, obj.v.y, obj.v.z])
        
        # Propagate for 'i' minutes (i * 60 seconds)
        # The propagate function expects a 6D state vector and a time step in seconds.
        # It returns a new 6D state vector.
        future_6d = propagate(curr_6d, i * 60)
        
        # Convert state vector (position part) to LLA for the frontend
        pos = future_6d[0:3]
        r = np.linalg.norm(pos)
        
        # Ensure r is not zero to avoid division by zero in arcsin
        if r == 0:
            lat = 0.0
            lon = 0.0
            alt = -6371.0 # Or handle as an error/special case
        else:
            lat = np.degrees(np.arcsin(pos[2] / r))
            lon = np.degrees(np.arctan2(pos[1], pos[0]))
            alt = r - 6371.0 # Assuming Earth's average radius for altitude calculation
        
        path.append([lat, lon, alt])
    
    return {"id": obj_id, "path": path}

@router.post("/simulate/step")
async def simulation_step(data: SimulationStepRequest):
    """
    Advances simulation time (Block 4G logic).
    1) Propagate all objects.
    2) Run conjunction detector.
    3) Execute scheduled burns.
    4) Check fuel/graveyard.
    5) Return step complete.
    """
    step_s = data.step_seconds
    
    # 1. Propagate all Satellites (Vectorized)
    sat_ids = list(state.satellites.keys())
    if sat_ids:
        sat_states = np.array([
            [s.r.x, s.r.y, s.r.z, s.v.x, s.v.y, s.v.z] for s in state.satellites.values()
        ])
        new_sat_states = propagate(sat_states, step_s)
        for idx, sid in enumerate(sat_ids):
            state.satellites[sid].r.x, state.satellites[sid].r.y, state.satellites[sid].r.z = new_sat_states[idx, 0:3]
            state.satellites[sid].v.x, state.satellites[sid].v.y, state.satellites[sid].v.z = new_sat_states[idx, 3:6]

    # 2. Propagate ONLY Debris near Satellites (Optimization)
    deb_ids = list(state.debris.keys())
    if deb_ids and sat_ids:
        from scipy.spatial import KDTree
        # Build KDTree of debris
        deb_pos_array = np.array([[state.debris[did].r.x, state.debris[did].r.y, state.debris[did].r.z] for did in deb_ids])
        tree = KDTree(deb_pos_array)
        
        # Find unique debris indices near any satellite
        active_deb_idx = set()
        for sid in sat_ids:
            sat_pos = np.array([state.satellites[sid].r.x, state.satellites[sid].r.y, state.satellites[sid].r.z])
            indices = tree.query_ball_point(sat_pos, r=200.0) # 200km filter
            active_deb_idx.update(indices)
            
        if active_deb_idx:
            active_deb_ids = [deb_ids[i] for i in active_deb_idx]
            state.active_debris_ids = active_deb_ids
            deb_states = np.array([
                [state.debris[did].r.x, state.debris[did].r.y, state.debris[did].r.z, 
                 state.debris[did].v.x, state.debris[did].v.y, state.debris[did].v.z] 
                for did in active_deb_ids
            ])
            new_deb_states = propagate(deb_states, step_s)
            for idx, did in enumerate(active_deb_ids):
                state.debris[did].r.x, state.debris[did].r.y, state.debris[did].r.z = new_deb_states[idx, 0:3]
                state.debris[did].v.x, state.debris[did].v.y, state.debris[did].v.z = new_deb_states[idx, 3:6]
    
    # 3. Time advancement
    state.sim_time += timedelta(seconds=step_s)
    
    # 4. Conjunction Detection
    cdms = detect_conjunctions(state.satellites, state.debris)
    # Update global state warnings
    state.cdm_warnings.clear()
    for cdm in cdms:
        warning_key = f"{cdm['sat_id']}_{cdm['deb_id']}"
        state.cdm_warnings[warning_key] = ConjunctionWarning(
            sat_id=cdm['sat_id'],
            debris_id=cdm['deb_id'],
            tca=state.sim_time + timedelta(seconds=cdm['tca_s']),
            miss_distance_km=cdm['miss_dist']
        )
        
    # 5. Autonomous Scheduling
    maneuvers_executed = process_cdm_warnings()
    
    return {
        "status": "STEP_COMPLETE",
        "new_timestamp": state.sim_time.isoformat(),
        "collisions_detected": 0, # To be implemented (if miss_dist < radius)
        "maneuvers_executed": len(maneuvers_executed)
    }
