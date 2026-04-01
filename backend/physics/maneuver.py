import numpy as np
from ..physics.propagator import ISP, G0, DRY_MASS

def rtn_to_eci(dv_rtn, r_vec, v_vec):
    """
    Converts a Delta-V vector from RTN frame to ECI frame.
    Block 4F implementation.
    """
    R_hat = r_vec / np.linalg.norm(r_vec)
    h = np.cross(r_vec, v_vec)
    N_hat = h / np.linalg.norm(h)
    T_hat = np.cross(N_hat, R_hat)
    
    # Rotation matrix M where rows are RTN basis in ECI
    # M maps ECI -> RTN. So M.T maps RTN -> ECI.
    M = np.array([R_hat, T_hat, N_hat])
    return M.T @ dv_rtn

def tsiolkovsky_delta_m(dv_mag, m_current):
    """
    Calculates fuel consumed (kg) for a given Delta-V.
    Block 4F implementation.
    """
    # delta_m = m_current * (1 - exp(-|dv| / (ISP * G0)))
    return m_current * (1 - np.exp(-dv_mag / (ISP * G0)))

def validate_burn(dv_vector_km_s):
    """
    Validates if burn is within MAX_DV limits.
    """
    dv_mag = np.linalg.norm(dv_vector_km_s)
    return dv_mag <= 0.015 # 15 m/s

def calculate_burn_effect(sat_state, dv_eci):
    """
    Computes the new state after an instantaneous burn.
    """
    new_v = np.array([sat_state.v.x, sat_state.v.y, sat_state.v.z]) + dv_eci
    # Fuel consumption (calculated elsewhere or here)
    return new_v
