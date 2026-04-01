# Orbital Insight - Autonomous Constellation Manager

**National Space Hackathon 2026**

## Statement of Purpose
**Orbital Insight** is an advanced, high-fidelity orbital propagation and autonomous constellation management platform. The system is designed to simulate, visualize, and actively protect a constellation of 50 active satellites operating in Low Earth Orbit (LEO) against a densely populated field of over 3,000 localized space debris objects. 

The core engineering objective of this implementation was to pioneer an overarching Mission Control interface that natively synchronizes highly complex physical $J_2$-perturbed orbital integrations with a low-latency WebGL visualization layer via a decoupled API and a Firebase real-time persistence layer.

---

## Core Architecture

The repository utilizes a strict decoupling between the mathematical physics heartbeat and the reactive web visualization, effectively bypassing the Global Interpreter Lock (GIL) and event-loop starvation protocols commonly found in asynchronous web frameworks rendering dense mathematics.

### Backend (Python/FastAPI)
- **High-Frequency Asynchronous Core**: Built on FastAPI traversing Uvicorn's ASGI interface.
- **De-coupled Physics Heartbeat**: A continuous `asyncio` background loop advancing the mission clock while yielding event control efficiently.
- **Thread Pool Delegation**: Dense CPU-bound iterations (NumPy vectors, KD-Tree constructs, RK4 integrators) are actively routed through `asyncio.to_thread` executors. This prevents blocking the primary REST API thread and guarantees millisecond-latency JSON payload resolution.

### Frontend (Next.js / React Three Fiber)
- **Web-native 3D Scene**: Real-time rendering of Earth, 50 satellites, and 3,000 kinematic dynamic debris nodes natively utilizing standard Three.js instantiated geometries to preserve 60-FPS rendering curves.
- **Dynamic Dual-Mode HUD**: A glassmorphic architectural UI composed with pristine Vanilla CSS and Tailwind allowing Mission Control analytics and purely kinematic Global Space Views.
- **Low-Latency Telemetry Polling**: An optimized `useSnapshot` custom hook orchestrates precise diffing on incoming arrays, ensuring re-renders occur purely on differential spatial velocities, retaining React DOM integrity.

### Data & Cloud Integration (Firebase / CelesTrak)
- **Firebase Admin SDK Uplink**: Secure service-account driven persistence logging states automatically to both the Firebase Real-Time Database (telemetry streaming) and Firestore (maneuver logging).
- **CelesTrak Telemetry Seed**: Active satellite parameters are natively parsed and seeded utilizing live operational TLE/Keplerian properties directly from CelesTrak.

---

## Mathematical Engine & Orbital Physics

The backend calculates pure Newtonian physics superimposed with primary Earth-system perturbations.

1. **J2 Oblateness Perturbation**: The equations of motion calculate exactly the non-spherical gravitational variance of Earth’s primary bulge ($J_2 = 1.08263 \times 10^{-3}$), shifting the classic Keplerian orbit into its real-world nodal precessions.
2. **Runge-Kutta Integrator (RK4)**: Pure continuous orbital mapping via robust 4th-order implementations calculating discrete integrations at massive time steps, vectorized purely via standard `numpy` matrices.
3. **KD-Tree Algorithmic Nearest-Neighbor Exclusion Bypass**:
    - Calculating $N^2$ collisions across 3,000+ un-indexed node geometries per 1.5 seconds is mathematically fatal to linear performance. 
    - The engine constructs a highly optimal Cartesian KD-Tree structure indexing all debris variables. The system strictly queries radial ball boundaries mathematically limited to $R = 200 \text{ km}$.
    - This limits predictive conjunction calculations strictly to the exact target subsets endangering the constellation, preventing useless O(N) orbital propagations.
4. **Time of Closest Approach (TCA)**: Micro level sub-routine sweeps detect precise intersection thresholds.

---

## Setup & Execution

### Prerequisites
- Python 3.9+
- Node.js 18+
- Active Firebase Project configured with a generated `firebase-adminsdk.json`

### Bare-Metal Local Testing

1. **Launch The Math/Physics Daemon (Backend)**
```bash
cd backend
python -m pip install -r ../requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*(The physics daemon will natively boot, seed CelesTrak data, index the KD-Tree logic, and initialize the telemetry endpoint at `http://localhost:8000/api/visualization/snapshot`)*

2. **Launch the Telemetry HUD (Frontend)**
```bash
cd frontend
npm install
npm run dev
```

### Containerized Deployment (Docker)

To bypass local dependency mapping for cloud deployment (e.g. AWS Fargate, Google Cloud Run):
```bash
docker build -t orbital-insight:latest .
docker run -p 8000:8000 -p 3000:3000 orbital-insight:latest
```

---

## Essential REST Endpoints

| Endpoint | Method | Response Payload | Description |
| :--- | :--- | :--- | :--- |
| `/api/visualization/snapshot` | `GET` | JSON | Primary kinematic telemetry stream for rendering nodes. |
| `/api/maneuver/plan` | `POST` | JSON | Ingests Delta-V maneuver execution requests to bypass CDM ranges. |
| `/api/telemetry/snapshot` | `GET` | JSON | Analytical statistical readout arrays for mission logs. |

---
**National Space Hackathon 2026** — Prepared exclusively for the Orbital Insight problem statement.
