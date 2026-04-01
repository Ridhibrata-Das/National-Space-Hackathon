from typing import Dict, List
from datetime import datetime
from .models.schemas import SpacecraftState, StateVector, ScheduledBurn, ConjunctionWarning, Vector3D
from .services.data_fetcher import fetch_debris_data, parse_gp_to_state
import asyncio
import numpy as np

EARTH_RADIUS_KM = 6378.137

# Global State Containers
satellites: Dict[str, SpacecraftState] = {}
debris: Dict[str, StateVector] = {}
cdm_warnings: Dict[str, ConjunctionWarning] = {}
maneuvers: List[ScheduledBurn] = []
active_debris_ids: List[str] = []
sim_time: datetime = datetime(2026, 1, 1, 0, 0, 0)
last_fetch_time: datetime = datetime.min
fetch_count_today: int = 0
is_initialized: bool = False

async def initialize_debris_data():
    global is_initialized, debris, satellites
    if is_initialized: return
    
    print("DEBUG: Global initialization started...")
    
    # 1. Fetch 50 Real-World Satellites
    try:
        from .services.data_fetcher import fetch_active_satellites
        sat_data = await fetch_active_satellites()
        sat_idx = 0
        
        for obj in sat_data:
            sid = obj.get("OBJECT_NAME", f"SAT-{sat_idx}")
            
            # Keplerian elements from CelesTrak JSON
            inc = np.radians(float(obj.get("INCLINATION", 0)))
            raan = np.radians(float(obj.get("RA_OF_ASC_NODE", 0)))
            e = float(obj.get("ECCENTRICITY", 0))
            arg_pe = np.radians(float(obj.get("ARG_OF_PERICENTER", 0)))
            ma = np.radians(float(obj.get("MEAN_ANOMALY", 0)))
            n_revs_per_day = float(obj.get("MEAN_MOTION", 15))
            
            # Mean motion in rad/s
            n = n_revs_per_day * 2 * np.pi / 86400.0
            
            # Semi-major axis (km) -> a = (mu / n^2)^(1/3)
            mu = 398600.4418
            a = (mu / (n**2))**(1/3)
            
            # Approximation for Eccentric Anomaly (E ~ M for small e)
            E = ma
            if e > 0.01:
                # Simple Newton-Raphson for E
                for _ in range(5):
                    E = E - (E - e * np.sin(E) - ma) / (1 - e * np.cos(E))
            
            # True Anomaly (nu)
            nu = 2 * np.arctan(np.sqrt((1 + e) / (1 - e)) * np.tan(E / 2))
            
            # Distance r
            r_mag = a * (1 - e * np.cos(E))
            
            # Position in orbital plane
            x_orb = r_mag * np.cos(nu)
            y_orb = r_mag * np.sin(nu)
            
            # Velocity in orbital plane
            h = np.sqrt(mu * a * (1 - e**2))
            p = a * (1 - e**2)
            vx_orb = -(mu / h) * np.sin(nu)
            vy_orb = (mu / h) * (e + np.cos(nu))
            
            # Rotation matrices
            cos_raan, sin_raan = np.cos(raan), np.sin(raan)
            cos_inc, sin_inc = np.cos(inc), np.sin(inc)
            cos_argpe, sin_argpe = np.cos(arg_pe), np.sin(arg_pe)
            
            # Transformation matrix from orbital to ECI (Active Z-X-Z rotation)
            R11 = cos_raan * cos_argpe - sin_raan * sin_argpe * cos_inc
            R12 = -cos_raan * sin_argpe - sin_raan * cos_argpe * cos_inc
            R21 = sin_raan * cos_argpe + cos_raan * sin_argpe * cos_inc
            R22 = -sin_raan * sin_argpe + cos_raan * cos_argpe * cos_inc
            R31 = sin_argpe * sin_inc
            R32 = cos_argpe * sin_inc
            
            # ECI Position
            x = R11 * x_orb + R12 * y_orb
            y = R21 * x_orb + R22 * y_orb
            z = R31 * x_orb + R32 * y_orb
            
            # ECI Velocity
            vx = R11 * vx_orb + R12 * vy_orb
            vy = R21 * vx_orb + R22 * vy_orb
            vz = R31 * vx_orb + R32 * vy_orb
            
            satellites[sid] = SpacecraftState(
                id=sid, type="SATELLITE",
                r=Vector3D(x=x, y=y, z=z),
                v=Vector3D(x=vx, y=vy, z=vz),
                fuel_kg=50.0, status="NOMINAL",
                last_updated=datetime.now()
            )
            sat_idx += 1
            
        print(f"DEBUG: Seeded {len(satellites)} REAL satellites.")
    except Exception as e:
        print(f"ERROR: Failed to initialize real satellites: {e}")

    # 2. Fetch or Generate Mass Debris
    try:
        raw_data = await fetch_debris_data()
        if raw_data:
            parsed_debris = parse_gp_to_state(raw_data)
            debris.update(parsed_debris)
            print(f"DEBUG: Seeded {len(debris)} REAL debris objects.")
        else:
            print("DEBUG: Fetch empty. Seeding 3000 SYNTHETIC debris...")
            for i in range(3000):
                if i % 1000 == 0:
                    await asyncio.sleep(0)  # Yield to event loop
                did = f"SYNTH-DEB-{i:05d}"
                r_mag = EARTH_RADIUS_KM + np.random.uniform(300, 2000)
                phi = np.random.uniform(0, 2*np.pi)
                theta = np.random.uniform(0, np.pi)
                debris[did] = StateVector(
                    id=did,
                    r=Vector3D(
                        x=r_mag * np.sin(theta) * np.cos(phi),
                        y=r_mag * np.sin(theta) * np.sin(phi),
                        z=r_mag * np.cos(theta)
                    ),
                    v=Vector3D(
                        x=np.random.uniform(-4, 4),
                        y=np.random.uniform(-4, 4),
                        z=np.random.uniform(-4, 4)
                    )
                )
            print(f"DEBUG: Seeded {len(debris)} synthetic objects.")
    except Exception as e:
        print(f"ERROR: Debris fetch/seed failed: {e}")

    is_initialized = True
    print("DEBUG: Simulation initialization complete.")

# Constants from Block 4C
GROUND_STATIONS = [
    {"id": "GS-001", "name": "ISTRAC_Bengaluru",    "lat":  13.0333, "lon":  77.5167, "elev_m":  820, "min_elev_deg":  5.0},
    {"id": "GS-002", "name": "Svalbard",             "lat":  78.2297, "lon":  15.4077, "elev_m":  400, "min_elev_deg":  5.0},
    {"id": "GS-003", "name": "Goldstone",            "lat":  35.4266, "lon": -116.8900,"elev_m": 1000, "min_elev_deg": 10.0},
    {"id": "GS-004", "name": "Punta_Arenas",         "lat": -53.1500, "lon": -70.9167, "elev_m":   30, "min_elev_deg":  5.0},
    {"id": "GS-005", "name": "IIT_Delhi_Ground_Node","lat":  28.5450, "lon":  77.1926, "elev_m":  225, "min_elev_deg": 15.0},
    {"id": "GS-006", "name": "McMurdo_Station",      "lat": -77.8463, "lon": 166.6682, "elev_m":   10, "min_elev_deg":  5.0},
]
