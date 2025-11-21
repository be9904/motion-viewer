# library imports
import numpy as np
from OpenGL.GL import *
# from OpenGL.GLU import *
import glfw
import quaternion

# local imports
import core
from .config import *

class Camera(core.Plugin):
    def __init__(self, window=None):
        # reference to program window
        self.wnd = window
        
        # camera position, rotation (Euler angles -> pitch, yaw, roll), up vector and target (lookAt)
        self.position = np.array([5.0, 5.0, 5.0], dtype=np.float32)
        self.rotation = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.target = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        
        # projection parameters
        self.fovy = np.radians(60.0)
        self.near = 0.1
        self.far = 100.0
        if self.wnd is not None:
            self.aspect = self.wnd.width / self.wnd.height
        else:
            self.aspect = 1.0
    
    # assemble all configurations and files
    def assemble(self):
        # export to shared data
        core.SharedData.export_data("camera", self)
        return

    # setup basic settings (window, gui, logs etc)
    def init(self):        
        # register glfw callbacks
        # if not self.wnd:
        #     raise Exception(f"{self.__class__.__name__}.init(): missing window reference")
        
        # glfw.set_key_callback(self.wnd.window, self.keyboard)
        # glfw.set_cursor_pos_callback(self.wnd.window, self.mouse_motion)
        # glfw.set_mouse_button_callback(self.wnd.window, self.mouse_button)
        # glfw.set_scroll_callback(self.wnd.window, self.mouse_scroll)
        
        # # print control hints to console
        # self.control_hint()
        
        return

    # executed every frame
    def update(self):
        # update aspect in case window resized -> change to on dirty callback
        self.aspect = self.wnd.width / self.wnd.height

        return

    # reset any modified parameters or files
    def reset(self):
        # reset position, rotation, up vector and target
        self.position[:] = np.array([5.0, 5.0, 5.0], dtype=np.float32)
        self.rotation[:] = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.up[:] = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.target[:] = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.last_mouse = None
        
        return

    # release runtime data
    def release(self):
        return