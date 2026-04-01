from fastapi import APIRouter
from .. import state
from datetime import datetime
import numpy as np

EARTH_RADIUS_KM = 6378.137

def eci_to_lla(r_eci, timestamp):
    """
    Simplified ECI to LLA conversion.
    """
    x, y, z = r_eci
    r = np.linalg.norm(r_eci)
    alt = r - EARTH_RADIUS_KM
    
    # Lon calculation (Simplified GST)
    epoch = datetime(2026, 1, 1)
    dt = (timestamp - epoch).total_seconds()
    gst = (dt % 86400) / 86400 * 360.0
    
    lon = (np.degrees(np.arctan2(y, x)) - gst + 180) % 360 - 180
    lat = np.degrees(np.arcsin(z / r))
    
    return lat, lon, alt

router = APIRouter()

@router.get("/visualization/snapshot")
async def get_snapshot(include_debris: bool = True):
    """
    Returns lat/lon/alt for all objects. (Block 4G)
    """
    sat_list = []
    for sat_id, sat in state.satellites.items():
        r_vec = [sat.r.x, sat.r.y, sat.r.z]
        lat, lon, alt = eci_to_lla(r_vec, state.sim_time)
        
        sat_list.append({
            "id": sat_id,
            "lat": lat,
            "lon": lon,
            "alt_km": alt,
            "fuel_kg": getattr(sat, 'fuel_kg', 48.0),
            "fuel_max_kg": 50.0,
            "status": getattr(sat, 'status', 'NOMINAL'),
            "dv_consumed_ms": 0.0
        })
        
    deb_cloud = []
    if include_debris:
        # Only return debris that are actually physically threatening the Active Satellites (KD-Tree matches)
        for deb_id in state.active_debris_ids:
            if deb_id in state.debris:
                deb = state.debris[deb_id]
                # Frontend expects ECI {r: {x, y, z}} for the high-perf points field
                deb_cloud.append({
                    "r": {
                        "x": deb.r.x,
                        "y": deb.r.y,
                        "z": deb.r.z
                    }
                })
            
    warnings_list = []
    for w in state.cdm_warnings.values():
        warnings_list.append({
            "sat_id": w.sat_id,
            "debris_id": w.debris_id,
            "tca": w.tca.isoformat(),
            "miss_distance_km": w.miss_distance_km,
            "status": getattr(w, 'status', 'PENDING_APPROVAL')
        })
        
    return {
        "timestamp": state.sim_time.isoformat(),
        "satellites": sat_list,
        "debris_cloud": deb_cloud,
        "cdm_warnings": warnings_list
    }
