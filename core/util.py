import numpy as np
import quaternion as qt

#####################################
# UTILITY FUNCTIONS
#####################################

def set_translate(v):
    T = np.zeros((4, 4), dtype=np.float32)
    T[0,3] = v[0]
    T[1,3] = v[1]
    T[2,3] = v[2]
    return T

def set_scale(v):
    S = np.zeros((4, 4), dtype=np.float32)
    S[0,0] = v[0]
    S[1,1] = v[1]
    S[2,2] = v[2]
    return S

def set_rotate(q):
    # convert to axis and angle
    q_x, q_y, q_z, q_w = q
    angle = 2 * np.arccos(q_w)
    q_s = np.sqrt(1 - q_w * q_w)
    if q_s < 1e-6:
        axis = np.array([1, 0, 0], dtype=np.float32)
    else:
        axis = np.array([q_x, q_y, q_z], dtype=np.float32) / q_s
    
    # build rotation matrix R
    R = np.zeros((4, 4), dtype=np.float32)
    c = np.cos(angle); s = np.sin(angle); x = axis[0]; y = axis[1]; z = axis[2]
    R[0,0] = x * x * (1 - c) + c;     R[0,1] = x * y * (1 - c) - z * s; R[0,2] = x * z * (1 - c) + y * s; R[0,3] = 0
    R[1,0] = x * y * (1 - c) + z * s; R[1,1] = y * y * (1 - c) + c;     R[1,2] = y * z * (1 - c) - x * s; R[1,3] = 0
    R[2,0] = x * z * (1 - c) - y * s; R[2,1] = y * z * (1 - c) + x * s; R[2,2] = z * z * (1 - c) + c;     R[2,3] = 0
    R[3,0] = 0;                       R[3,1] = 0;                       R[3,2] = 0;                       R[3,3] = 1
    
    return R

def get_model_matrix(position, rotation, scale): # rotation is quaternion    
    if rotation.shape == ():
        # Convert numpy-quaternion [w, x, y, z] to float array
        q_vec = qt.as_float_array(rotation)
        # Reorder to [x, y, z, w] because set_rotate expects (x, y, z, w)
        rotation = np.array([q_vec[1], q_vec[2], q_vec[3], q_vec[0]], dtype=np.float32)

    if rotation.shape[0] != 4:
        raise ValueError("rotation must be passed as quaternions")
    
    T = set_translate(position)
    R = set_rotate(rotation)
    S = set_scale(scale)
    
    M = T @ R @ S
    
    return M # P @ V @ M @ local

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm