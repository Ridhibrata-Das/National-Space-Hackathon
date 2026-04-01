from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import telemetry, simulate, maneuver, visualization
import os

app = FastAPI(title="NSH 2026 Autonomous Constellation Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import asyncio
from .api.simulate import simulation_step
from .api.visualization import get_snapshot
from .firebase_client import sync_state_to_firebase

async def physics_heartbeat():
    print("DEBUG: Physics heartbeat started.")
    while True:
        try:
            # Advance simulation by 10 seconds every 1.5 seconds real-time
            from .models.schemas import SimulationStepRequest
            req = SimulationStepRequest(step_seconds=10.0)
            
            import asyncio
            from .api.simulate import simulation_step
            await simulation_step(req)
            
            # Yield control frequently to allow HTTP requests to process
            await asyncio.sleep(0.01)
            
            # Get latest snapshot (excluding mass debris for RTDB efficiency)
            snapshot = await get_snapshot(include_debris=False)

            # Sync to Firebase
            await sync_state_to_firebase(snapshot)
            
            await asyncio.sleep(1.5)
        except Exception as e:
            print(f"ERROR: Physics heartbeat failed: {e}")
            await asyncio.sleep(5.0)

@app.on_event("startup")
async def startup_event():
    from .state import initialize_debris_data
    await initialize_debris_data()
    asyncio.create_task(physics_heartbeat())

# Mount Routers (Block 4G)
app.include_router(telemetry.router, prefix="/api")
app.include_router(simulate.router, prefix="/api")
app.include_router(maneuver.router, prefix="/api")
app.include_router(visualization.router, prefix="/api")

# Static Frontend Mounting (Phase 4)
if os.path.exists("./frontend/out"):
    app.mount("/", StaticFiles(directory="./frontend/out", html=True), name="static")

@app.get("/health")
async def health_check():
    return {"status": "OK", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
