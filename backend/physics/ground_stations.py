import numpy as np
from datetime import datetime
from ..state import GROUND_STATIONS
from .propagator import RE  # We'll need Earth radius

# Constants
OMEGA_E = 7.2921150e-5  # Earth rotation rate in rad/s

def llh_to_ecef(lat_deg, lon_deg, elev_m):
    """Converts Geodetic coordinates to ECEF."""
    lat = np.radians(lat_deg)
    lon = np.radians(lon_deg)
    alt = elev_m / 1000.0  # Convert to km
    
    # Simple spherical Earth for initial implementation (as per common hackathon standards)
    # But for J2 accuracy, we should use RE. 
    # The reference says RE = 6378.137 km (equatorial)
    
    r = RE + alt
    x = r * np.cos(lat) * np.cos(lon)
    y = r * np.cos(lat) * np.sin(lon)
    z = r * np.sin(lat)
    return np.array([x, y, z])

def ecef_to_eci(r_ecef, sim_time_s):
    """Rotates ECEF vector to ECI based on simulation time."""
    theta = OMEGA_E * sim_time_s
    c, s = np.cos(theta), np.sin(theta)
    
    # Rotation matrix around Z-axis
    Rz = np.array([
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ])
    return Rz @ r_ecef

def get_elevation_angle(sat_eci, gs_eci, gs_lat_deg, gs_lon_deg, sim_time_s):
    """Calculates elevation angle of satellite from ground station."""
    # Vector from GS to Sat
    p = sat_eci - gs_eci
    dist = np.linalg.norm(p)
    if dist == 0: return 90.0
    
    # Local Zenith vector at GS (ECEF zenith rotated to ECI)
    # Zenith in ECEF is just the normalized GS position (for spherical Earth)
    zenith_ecef = gs_eci / np.linalg.norm(gs_eci) # Since we used spherical for llh_to_ecef
    
    # Wait, if we use spherical, zenith is just the GS vector unitized.
    # Angle between p and zenith
    dot_prod = np.dot(p, zenith_ecef)
    cos_zeta = dot_prod / dist
    zeta = np.arccos(np.clip(cos_zeta, -1.0, 1.0)) # zenith angle
    
    elev_angle = 90.0 - np.degrees(zeta)
    return elev_angle

def has_los(sat_eci, sim_time_s):
    """Checks if any ground station has LOS to the satellite."""
    for gs in GROUND_STATIONS:
        gs_ecef = llh_to_ecef(gs["lat"], gs["lon"], gs["elev_m"])
        gs_eci = ecef_to_eci(gs_ecef, sim_time_s)
        
        elev = get_elevation_angle(sat_eci, gs_eci, gs["lat"], gs["lon"], sim_time_s)
        if elev >= gs["min_elev_deg"]:
            return True
    return False
