# library imports
import numpy as np
import quaternion as qt

# local imports
import core


def cursor_to_ndc(cursor, window_size):
    """
    Convert window cursor position to normalized device coordinates [-1, 1]
    
    Args:
        cursor: tuple or array of (x, y) window coordinates
        window_size: tuple or array of (width, height)
    
    Returns:
        numpy array of [x, y] in NDC coordinates [-1, 1]
    """
    # normalize window pos to [0,1]^2
    npos = np.array([
        float(cursor[0]) / float(window_size[0] - 1),
        float(cursor[1]) / float(window_size[1] - 1)
    ], dtype=np.float32)
    
    # normalize window pos to [-1,1]^2 with vertical flipping
    # vertical flipping: window coordinate system defines y from
    # top to bottom, while the trackball from bottom to top
    return np.array([
        npos[0] * 2.0 - 1.0,
        1.0 - npos[1] * 2.0
    ], dtype=np.float32)


def translate_matrix(t):
    """
    Create a 4x4 translation matrix
    
    Args:
        t: translation vector (x, y, z)
    
    Returns:
        4x4 translation matrix
    """
    T = np.eye(4, dtype=np.float32)
    T[:3, 3] = np.array(t, dtype=np.float32)
    return T


def rotate_matrix(axis, angle):
    """
    Create a 4x4 rotation matrix from axis-angle representation
    
    Args:
        axis: rotation axis vector (x, y, z), will be normalized
        angle: rotation angle in radians
    
    Returns:
        4x4 rotation matrix
    """
    axis = np.array(axis, dtype=np.float32)
    axis = core.normalize(axis)
    
    # Create quaternion from axis-angle
    q = qt.quaternion(
        np.cos(angle / 2.0),
        axis[0] * np.sin(angle / 2.0),
        axis[1] * np.sin(angle / 2.0),
        axis[2] * np.sin(angle / 2.0)
    )
    
    # Convert quaternion to rotation matrix
    R3 = qt.as_rotation_matrix(q)
    R = np.eye(4, dtype=np.float32)
    R[:3, :3] = R3
    return R


def look_at_matrix(eye, at, up):
    """
    Create a 4x4 look-at view matrix
    
    Args:
        eye: eye position (x, y, z)
        at: target position (x, y, z)
        up: up vector (x, y, z)
    
    Returns:
        4x4 view matrix
    """
    eye = np.array(eye, dtype=np.float32)
    at = np.array(at, dtype=np.float32)
    up = np.array(up, dtype=np.float32)
    
    f = core.normalize(at - eye)
    s = core.normalize(np.cross(f, up))
    u = np.cross(s, f)
    
    M = np.eye(4, dtype=np.float32)
    M[0, :3] = s
    M[1, :3] = u
    M[2, :3] = -f
    M[:3, 3] = -np.array([eye @ s, eye @ u, eye @ -f])
    
    return M


class Trackball:
    def __init__(self, rot_scale=1.0):
        """
        Initialize trackball
        
        Args:
            rot_scale: controls how much movement is applied (default: 1.0)
        """
        self.b_tracking = False
        self.button = 0  # check button down
        self.mods = 0  # shift or ctrl
        self.scale = rot_scale  # controls how much movement is applied
        self.view_matrix0 = None  # initial view matrix
        self.m0 = None  # the last mouse position (vec2)
        self.prev_cursor = np.array([0.0, 0.0, 1.0], dtype=np.float32)  # saves previous cursor location
    
    def is_tracking(self):
        """Check if trackball is currently tracking"""
        return self.b_tracking
    
    def begin(self, view_matrix, m):
        """
        Begin trackball tracking
        
        Args:
            view_matrix: current 4x4 view matrix
            m: mouse position (x, y) in window coordinates
        """
        self.b_tracking = True  # enable trackball tracking
        self.m0 = np.array(m, dtype=np.float32)  # save current mouse position
        self.view_matrix0 = np.array(view_matrix, dtype=np.float32)  # save current view matrix
        self.prev_cursor = np.array([0.0, 0.0, 1.0], dtype=np.float32)
    
    def end(self):
        """End trackball tracking"""
        self.b_tracking = False
    
    def update_rotation(self, m, eye, at, up):
        """
        Update camera rotation using trackball
        
        Args:
            m: current mouse position (x, y) in window coordinates
            eye: eye position (x, y, z), will be modified
            at: target position (x, y, z), will be modified
            up: up vector (x, y, z), will be modified
        
        Returns:
            4x4 view matrix
        """
        # project a 2D mouse position to a unit sphere
        p0 = np.array([0.0, 0.0, 1.0], dtype=np.float32)  # reference position on sphere
        
        # displacement
        m_vec = np.array(m, dtype=np.float32)
        m0_vec = np.array(self.m0, dtype=np.float32)
        p1 = np.array([m_vec[0] - m0_vec[0], m_vec[1] - m0_vec[1], 0.0], dtype=np.float32)
        
        if not self.b_tracking or np.linalg.norm(p1) < 0.0001:
            return self.view_matrix0  # ignore subtle movement
        
        # back-project z=0 onto the unit sphere
        length2 = p1[0] * p1[0] + p1[1] * p1[1]
        if length2 >= 1.0:
            p1[2] = 0.0
            p1 = core.normalize(p1)
        else:
            p1[2] = np.sqrt(np.maximum(0.0, 1.0 - length2))
            p1 = core.normalize(p1)
        
        # view -> world: mat3(view_matrix0).transpose() * prevCursor.cross(p1)
        view_rot = self.view_matrix0[:3, :3].T  # transpose of rotation part
        v = view_rot @ np.cross(self.prev_cursor, p1)
        
        # compute rotation angle
        v_length = np.linalg.norm(v)
        theta = np.arcsin(np.clip(v_length, -1.0, 1.0)) * self.scale * 0.1
        
        # create transformation: translate(at) * rotate(v.normalize(), -theta) * translate(-at)
        v_normalized = core.normalize(v)
        trt = translate_matrix(at) @ rotate_matrix(v_normalized, -theta) @ translate_matrix(-at)
        
        # transform eye, at, up
        eye4 = np.append(eye, 1.0)
        at4 = np.append(at, 1.0)
        up4 = np.append(up, 1.0)
        
        eye4 = trt @ eye4
        at4 = trt @ at4
        up4 = trt @ up4
        
        eye[:] = eye4[:3]
        at[:] = at4[:3]
        up[:] = up4[:3]
        
        self.prev_cursor = p1
        self.scale = np.linalg.norm(eye - at) * 0.5
        
        return look_at_matrix(eye, at, up)
    
    def update_pan(self, m, eye, at, up):
        """
        Update camera pan using trackball
        
        Args:
            m: current mouse position (x, y) in window coordinates
            eye: eye position (x, y, z), will be modified
            at: target position (x, y, z), will be modified
            up: up vector (x, y, z), will be modified (not used but kept for API consistency)
        
        Returns:
            4x4 view matrix
        """
        # displacement
        m_vec = np.array(m, dtype=np.float32)
        m0_vec = np.array(self.m0, dtype=np.float32)
        p1 = np.array([m_vec[0] - m0_vec[0], m_vec[1] - m0_vec[1], 0.0], dtype=np.float32)
        
        if not self.b_tracking or np.linalg.norm(p1) < 0.0001:
            return self.view_matrix0  # ignore subtle movement
        
        # back-project z=0 onto the unit sphere
        length2 = p1[0] * p1[0] + p1[1] * p1[1]
        if length2 >= 1.0:
            p1[2] = 0.0
            p1 = core.normalize(p1)
        else:
            p1[2] = np.sqrt(np.maximum(0.0, 1.0 - length2))
            p1 = core.normalize(p1)
        
        # compute pan offset in view space (x, y only, z=0)
        vpan_offset = p1 - self.prev_cursor
        vpan_offset[2] = 0.0
        
        # transform view space to world space: mat3(view_matrix0.transpose()) * vpan_offset * scale
        view_rot = self.view_matrix0[:3, :3].T  # transpose of rotation part
        wpan_offset = view_rot @ vpan_offset * self.scale
        
        # move eye and target
        eye[:] = eye - wpan_offset
        at[:] = at - wpan_offset
        
        self.prev_cursor = p1
        self.scale = np.linalg.norm(eye - at) * 0.5
        
        return look_at_matrix(eye, at, up)
    
    def update_zoom(self, m, eye, at, up):
        """
        Update camera zoom using trackball
        
        Args:
            m: current mouse position (x, y) in window coordinates
            eye: eye position (x, y, z), will be modified
            at: target position (x, y, z), will be modified (not used but kept for API consistency)
            up: up vector (x, y, z), will be modified (not used but kept for API consistency)
        
        Returns:
            4x4 view matrix
        """
        # displacement
        m_vec = np.array(m, dtype=np.float32)
        m0_vec = np.array(self.m0, dtype=np.float32)
        p1 = np.array([m_vec[0] - m0_vec[0], m_vec[1] - m0_vec[1], 0.0], dtype=np.float32)
        
        if not self.b_tracking or np.linalg.norm(p1) < 0.0001:
            return self.view_matrix0  # ignore subtle movement
        
        # back-project z=0 onto the unit sphere
        length2 = p1[0] * p1[0] + p1[1] * p1[1]
        if length2 >= 1.0:
            p1[2] = 0.0
            p1 = core.normalize(p1)
        else:
            p1[2] = np.sqrt(np.maximum(0.0, 1.0 - length2))
            p1 = core.normalize(p1)
        
        # compute zoom offset in view space (only y component)
        vzoom_offset = np.array([0.0, 0.0, p1[1] - self.prev_cursor[1]], dtype=np.float32)
        
        # transform view space to world space: mat3(view_matrix0.transpose()) * vzoom_offset * (-scale)
        view_rot = self.view_matrix0[:3, :3].T  # transpose of rotation part
        wzoom = view_rot @ vzoom_offset * (-self.scale)
        
        # move eye
        eye[:] = eye - wzoom
        
        self.prev_cursor = p1
        self.scale = np.linalg.norm(eye - at) * 0.5
        
        return look_at_matrix(eye, at, up)

