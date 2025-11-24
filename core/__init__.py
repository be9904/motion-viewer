from abc import ABC, abstractmethod
from OpenGL.GL import glViewport
import glfw
import numpy as np
import quaternion as qt

from .shader import Shader

#####################################
# PLUGIN
#####################################

class Plugin(ABC):
    def __init__(self):
        print(f"{self.__class__.__name__}")

    # assemble all configurations and files
    @abstractmethod
    def assemble(self, import_data):
        pass

    # setup basic settings (window, gui, logs etc)
    @abstractmethod
    def init(self):
        pass

    # executed every frame
    @abstractmethod
    def update(self):
        pass
    
    # executed at end of frame, after all plugin updates have looped
    def post_update(self):
        pass

    # reset any modified parameters or files
    @abstractmethod
    def reset(self):
        pass

    # release runtime data
    @abstractmethod
    def release(self):
        pass

class SharedData:
    _data = {}

    @classmethod
    def export_data(cls, name, value):
        cls._data[name] = value

    @classmethod
    def import_data(cls, name):
        return cls._data.get(name, None)
    
    @classmethod # for debugging
    def list_data(cls):
        print(cls._data)

#####################################
# TRANSFORMATION
#####################################

def set_translate(v):
    T = np.identity(4, dtype=np.float32)
    T[0,3] = v[0]
    T[1,3] = v[1]
    T[2,3] = v[2]
    return T

def get_model_matrix(position, rotation, scale): # rotation is in quaternions
    T = np.eye(4, dtype=np.float32)
    T[:3, 3] = position

    R3 = qt.as_rotation_matrix(rotation)
    R = np.eye(4, dtype=np.float32)
    R[:3, :3] = R3

    S = np.eye(4, dtype=np.float32)
    S[0,0] = scale[0]
    S[1,1] = scale[1]
    S[2,2] = scale[2]

    return T @ R @ S

def get_view_matrix(camera):
    eye = np.array(camera.position, dtype=np.float32)
    at = np.array(camera.target, dtype=np.float32)
    up = np.array(camera.up, dtype=np.float32)

    f = normalize(at - eye)
    s = normalize(np.cross(f, up))
    u = np.cross(s, f)

    M = np.eye(4, dtype=np.float32)
    M[0, :3] = s
    M[1, :3] = u
    M[2, :3] = -f
    M[:3, 3] = -np.array([eye @ s, eye @ u, eye @ -f])

    return M

def get_projection_matrix(camera):
    fovy = camera.fovy
    aspect = camera.aspect
    near = camera.near
    far = camera.far

    f = 1.0 / np.tan(fovy / 2)
    P = np.zeros((4,4), dtype=np.float32)
    P[0,0] = f / aspect
    P[1,1] = f
    P[2,2] = (far + near) / (near - far)
    P[2,3] = (2 * far * near) / (near - far)
    P[3,2] = -1
    
    return P

def get_mvp_matrix(position, rotation, scale, camera):
    M = get_model_matrix(position, rotation, scale)
    V = get_view_matrix(camera)
    P = get_projection_matrix(camera)
    return P @ V @ M

#####################################
# USER CALLBACK FUNCTIONS
#####################################

def resize(window, width=1920, height=1080): # resize glfw window
    glViewport(0, 0, width, height)

def keyboard(window, key, scancode, action, mods): # keyboard callbacks
    if action == glfw.PRESS:
        print('key press')
    if action == glfw.RELEASE:
        print('key released')
    return

def mouse(window, button, action, mods): # mouse interactions
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            print("Enable LMB Functionality")
        if action == glfw.RELEASE:
            print("Disable LMB Functionality")

    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            print("Enable RMB Functionality")
        if action == glfw.RELEASE:
            print("Disable RMB Functionality")

    if button == glfw.MOUSE_BUTTON_MIDDLE:
        if action == glfw.PRESS:
            print("Enable MMB Functionality")
        if action == glfw.RELEASE:
            print("Disable MMB Functionality")
    return

def cursor(window, x, y): # cursor position
    return

#####################################
# UTILITY FUNCTIONS
#####################################

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm