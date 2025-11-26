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

class Object:
    def __init__(self, name):
        self.name = name # name of Object (required)
        self.components = {} # non-plugins
        self.plugins = {} # plugins
        self.parent = None # parent Object
        self.children = [] # list of child Objects

    def add_component(self, name, comp):
        if isinstance(comp, Plugin):
            raise TypeError("Use add_plugin(plugin_name) instead.")

        if isinstance(comp, Object):
            raise TypeError("An Object cannot be added as a component")
        
        if name in self.objects:
            raise KeyError(f"Object with name '{name}' already exists")
        
        self.objects[name] = comp

    def add_plugin(self, name, plugin):
        if not isinstance(plugin, Plugin):
            raise TypeError("Object must inherit from Plugin")

        if isinstance(plugin, Object):
            raise TypeError("An Object cannot be added as a Plugin")
        
        if name in self.plugins:
            raise KeyError(f"Plugin with name '{name}' already exists")
        
        self.plugins[name] = plugin

    def set_parent(self, obj):
        if not isinstance(obj, Object):
            raise TypeError("Cannot set non-Object as a parent")
        
        self.parent = obj

    def set_child(self, obj):
        if not isinstance(obj, Object):
            raise TypeError("Cannot set non-Object as a parent")
        
        self.children.append(obj)

#####################################
# TRANSFORMATION
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
    if rotation.shape[0] != 4:
        raise ValueError("rotation must be passed as quaternions")
    
    T = set_translate(position)
    R = set_rotate(rotation)
    S = set_scale(scale)
    
    M = T @ R @ S
    
    return M # P @ V @ M @ local

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