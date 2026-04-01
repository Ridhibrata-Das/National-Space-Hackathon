import httpx
import json
import os
from typing import List, Dict
import numpy as np

CELESTRAK_DEBRIS_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=debris&FORMAT=json"
CACHE_FILE = "debris_cache.json"

from datetime import datetime, timedelta
from .. import state

async def fetch_debris_data():
    """Fetch debris data from CelesTrak with 5x/day throttling."""
    now = datetime.now()
    
    # Check if we should fetch (limit 5/day)
    if state.fetch_count_today >= 5 and now.date() == state.last_fetch_time.date():
        print("DEBUG: Fetch limit reached for today. Using local cache/state.")
        return None

    print(f"DEBUG: Starting debris data fetch (Count: {state.fetch_count_today + 1}/5)...")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(CELESTRAK_DEBRIS_URL)
            if response.status_code == 200:
                data = response.json()
                state.fetch_count_today += 1 if now.date() == state.last_fetch_time.date() else 1
                state.last_fetch_time = now
                
                truncated_data = data[:10000] # Cap at 10k for stability
                with open(CACHE_FILE, "w") as f:
                    json.dump(truncated_data, f)
                return truncated_data
    except Exception as e:
        print(f"ERROR: Fetch failed: {e}")
    
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return []

CELESTRAK_ACTIVE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json"
ACTIVE_CACHE_FILE = "active_sat_cache.json"

async def fetch_active_satellites():
    """Fetch 50 active satellites from CelesTrak."""
    if os.path.exists(ACTIVE_CACHE_FILE):
        with open(ACTIVE_CACHE_FILE, "r") as f:
            return json.load(f)

    print("DEBUG: Fetching 50 active satellites from CelesTrak...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(CELESTRAK_ACTIVE_URL)
            if response.status_code == 200:
                data = response.json()
                subset = data[:50] # Take first 50
                with open(ACTIVE_CACHE_FILE, "w") as f:
                    json.dump(subset, f)
                return subset
    except Exception as e:
        print(f"ERROR: Failed to fetch active satellites: {e}")
    return []

def parse_gp_to_state(gp_data: List[Dict]):
    """Convert TLE/GP data to state vectors (Simplified for demo)."""
    # In a real app, we'd use sgp4. Here we simulate random initial states for the demo
    # but use the IDs from the real data.
    states = {}
    for obj in gp_data:
        obj_id = obj.get("OBJECT_ID") or obj.get("OBJECT_NAME")
        if not obj_id: continue
        
        # Random initial state for simulation
        r = np.random.uniform(6800, 7500)
        phi = np.random.uniform(0, 2*np.pi)
        theta = np.random.uniform(0, np.pi)
        
        states[obj_id] = {
            "id": obj_id,
            "type": "DEBRIS",
            "r": {
                "x": r * np.sin(theta) * np.cos(phi),
                "y": r * np.sin(theta) * np.sin(phi),
                "z": r * np.cos(theta)
            },
            "v": {
                "x": np.random.uniform(-5, 5),
                "y": np.random.uniform(-5, 5),
                "z": np.random.uniform(-5, 5)
            }
        }
    return states
