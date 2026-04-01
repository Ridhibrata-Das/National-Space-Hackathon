import numpy as np
from scipy.spatial import KDTree
from .. import state
from ..physics.propagator import propagate, propagate_trajectory

def find_tca(sat_state, deb_state, start_time_s, duration_s=120, coarse_step=5, fine_step=1):
    """
    Finds Time of Closest Approach (TCA) between a satellite and a debris object.
    Phase 2 logic from Block 4D.
    """
    # 1. Coarse scan
    trajectory_sat = propagate_trajectory(sat_state, duration_s, coarse_step)
    trajectory_deb = propagate_trajectory(deb_state, duration_s, coarse_step)
    
    min_dist = float('inf')
    min_idx = -1
    
    for i in range(len(trajectory_sat)):
        d = np.linalg.norm(trajectory_sat[i][:3] - trajectory_deb[i][:3])
        if d < min_dist:
            min_dist = d
            min_idx = i
            
    if min_idx == -1: return None, float('inf')
    
    # 2. Refinement window
    t_min = max(0, (min_idx - 1) * coarse_step)
    t_max = min(duration_s, (min_idx + 1) * coarse_step)
    
    # Simple binary/linear search for refinement in the window
    # Search every 'fine_step' inside the [t_min, t_max] window
    curr_t = t_min
    refined_min_dist = float('inf')
    refined_tca_t = t_min
    
    while curr_t <= t_max:
        s_sat = propagate(sat_state, curr_t)
        s_deb = propagate(deb_state, curr_t)
        d = np.linalg.norm(s_sat[:3] - s_deb[:3])
        if d < refined_min_dist:
            refined_min_dist = d
            refined_tca_t = curr_t
        curr_t += fine_step
        
    return refined_tca_t, refined_min_dist

def detect_conjunctions(satellites, debris, threshold_km=0.1, filter_radius=200.0):
    """
    Two-Phase Detection (Block 4D).
    Phase 1: Spatial filter with KDTree.
    Phase 2: TCA search on candidates.
    """
    if not satellites or not debris:
        return []
    
    # Phase 1: Spatial Filter (Current Tiers)
    deb_ids = list(debris.keys())
    deb_positions = np.array([debris[id_].r.dict().values() for id_ in deb_ids]) # Assuming r is x,y,z
    # Better: just use the vector directly
    deb_pos_array = np.array([[debris[id_].r.x, debris[id_].r.y, debris[id_].r.z] for id_ in deb_ids])
    
    tree = KDTree(deb_pos_array)
    
    cdms = []
    
    for sat_id, sat in satellites.items():
        sat_pos = np.array([sat.r.x, sat.r.y, sat.r.z])
        nearby_indices = tree.query_ball_point(sat_pos, r=filter_radius)
        
        for idx in nearby_indices:
            deb_id = deb_ids[idx]
            deb = debris[deb_id]
            
            # Phase 2: TCA Search
            sat_6d = np.array([sat.r.x, sat.r.y, sat.r.z, sat.v.x, sat.v.y, sat.v.z])
            deb_6d = np.array([deb.r.x, deb.r.y, deb.r.z, deb.v.x, deb.v.y, deb.v.z])
            
            tca_t, miss_dist = find_tca(sat_6d, deb_6d, 0) # relative to current sim time
            
            if miss_dist < threshold_km:
                cdms.append({
                    "sat_id": sat_id,
                    "deb_id": deb_id,
                    "tca_s": tca_t,
                    "miss_dist": miss_dist
                })
                
    return cdms
