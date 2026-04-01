import numpy as np

# Physical Constants (Block 4B)
MU = 398600.4418  # km^3/s^2
RE = 6378.137     # km
J2 = 1.08263e-3   # dimensionless
G0 = 9.80665e-3   # km/s^2
ISP = 300.0       # seconds
DRY_MASS = 500.0  # kg
INIT_FUEL = 50.0  # kg
MAX_DV = 0.015    # km/s
COOLDOWN = 600.0  # seconds

def j2_acceleration(r_vec: np.ndarray) -> np.ndarray:
    """Calculates J2 perturbation acceleration (Vectorized)."""
    # r_vec can be (3,) or (N, 3)
    if r_vec.ndim == 1:
        r = np.linalg.norm(r_vec)
        if r == 0: return np.zeros(3)
        x, y, z = r_vec
        r2 = r**2
        z2 = z**2
        factor = (1.5 * J2 * MU * RE**2) / (r**5)
        return factor * np.array([x * (5 * z2 / r2 - 1), y * (5 * z2 / r2 - 1), z * (5 * z2 / r2 - 3)])
    else:
        # Vectorized (N, 3)
        r = np.linalg.norm(r_vec, axis=1, keepdims=True)
        r[r == 0] = 1e-9 # Avoid division by zero
        x = r_vec[:, 0:1]
        y = r_vec[:, 1:2]
        z = r_vec[:, 2:3]
        r2 = r**2
        z2 = z**2
        factor = (1.5 * J2 * MU * RE**2) / (r**5)
        ax = x * (5 * z2 / r2 - 1)
        ay = y * (5 * z2 / r2 - 1)
        az = z * (5 * z2 / r2 - 3)
        return factor * np.concatenate([ax, ay, az], axis=1)

def equations_of_motion(state_6d: np.ndarray) -> np.ndarray:
    """Computes derivative of state vector (Vectorized)."""
    # state_6d can be (6,) or (N, 6)
    if state_6d.ndim == 1:
        r_vec = state_6d[0:3]
        v_vec = state_6d[3:6]
        r = np.linalg.norm(r_vec)
        a_grav = (-MU / r**3) * r_vec
        a_j2 = j2_acceleration(r_vec)
        return np.concatenate([v_vec, a_grav + a_j2])
    else:
        # Vectorized (N, 6)
        r_vec = state_6d[:, 0:3]
        v_vec = state_6d[:, 3:6]
        r = np.linalg.norm(r_vec, axis=1, keepdims=True)
        r[r == 0] = 1e-9
        a_grav = (-MU / r**3) * r_vec
        a_j2 = j2_acceleration(r_vec)
        return np.concatenate([v_vec, a_grav + a_j2], axis=1)

def rk4_step(state_6d: np.ndarray, dt: float) -> np.ndarray:
    """Single RK4 integration step."""
    k1 = equations_of_motion(state_6d)
    k2 = equations_of_motion(state_6d + 0.5 * dt * k1)
    k3 = equations_of_motion(state_6d + 0.5 * dt * k2)
    k4 = equations_of_motion(state_6d + dt * k3)
    
    return state_6d + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

def propagate(state: np.ndarray, duration_s: float, dt: float = 10.0) -> np.ndarray:
    """Propagates state over duration_s using dt sub-steps."""
    num_steps = int(duration_s // dt)
    curr_state = state.copy()
    
    for _ in range(num_steps):
        curr_state = rk4_step(curr_state, dt)
    
    # Handle remaining time
    remainder = duration_s % dt
    if remainder > 0:
        curr_state = rk4_step(curr_state, remainder)
        
    return curr_state

def propagate_trajectory(state: np.ndarray, total_s: float, sample_interval: float = 60.0) -> list[np.ndarray]:
    """Returns a list of state snapshots over total_s duration."""
    num_samples = int(total_s // sample_interval)
    trajectory = [state.copy()]
    curr_state = state.copy()
    
    for _ in range(num_samples):
        curr_state = propagate(curr_state, sample_interval)
        trajectory.append(curr_state.copy())
        
    return trajectory

if __name__ == "__main__":
    # Test LEO satellite: altitude ~400km
    # Velocity for circular orbit: sqrt(MU / r)
    alt = 400.0
    r_mag = RE + alt
    v_mag = np.sqrt(MU / r_mag)
    
    test_state = np.array([r_mag, 0.0, 0.0, 0.0, v_mag, 0.0])
    
    # One full orbit ~90 mins (5400s)
    orbit_time = 2 * np.pi * np.sqrt(r_mag**3 / MU)
    print(f"Propagating for one orbit: {orbit_time:.2f} seconds")
    
    final_state = propagate(test_state, orbit_time)
    
    error = np.linalg.norm(final_state[0:3] - test_state[0:3])
    print(f"Final state after one orbit: {final_state}")
    print(f"Closure error: {error:.4f} km")
