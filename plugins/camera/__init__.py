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
        # reference of window for aspect update
        self.wnd = None
        
        # eye, at, up vector (lookAt)
        self.eye = np.array([5.0, 5.0, 5.0], dtype=np.float32) # position
        self.at = np.array([0.0, 0.0, 0.0], dtype=np.float32) # target
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32) # up direction
        self.view = self.look_at()
        
        # projection parameters
        self.fovy = np.radians(60.0)
        self.aspect = self.wnd.width / self.wnd.height if self.wnd is not None else 16.0 / 9.0
        self.near = 0.1
        self.far = 100.0
        self.projection = self.perspective()
        
        # export after creation
        core.SharedData.export_data("camera", self)

    def look_at(self):
        # define forward, right and true up
        n = self.eye - self.at
        u = np.cross(self.up, n)
        v = np.cross(n, u)
        
        # normalize
        n /= np.linalg.norm(n)
        u /= np.linalg.norm(u)
        v /= np.linalg.norm(v)
        
        # build matrix
        view = np.eye(4, dtype=np.float32)
        view[0, 0:3] = u
        view[1, 0:3] = v
        view[2, 0:3] = n
        view[0, 3] = -np.dot(u, self.eye)
        view[1, 3] = -np.dot(v, self.eye)
        view[2, 3] = -np.dot(n, self.eye)
        
        return view
    
    def perspective(self):
        projection = np.zeros((4, 4), dtype=np.float32)
        
        projection[1,1] = 1 / np.tan(self.fovy / 2.0)
        projection[0,0] = projection[1,1] / self.aspect
        projection[2,2] = (self.near + self.far) / (self.near - self.far)
        projection[2,3] = (2 * self.near * self.far) / (self.near - self.far)
        projection[3,2] = -1
        projection[3,3] = 0
        
        return projection
            
    #####################################
    # Callback Functions
    #####################################
    
    # assemble all configurations and files
    def assemble(self):
        # imports
        self.wnd = core.SharedData.import_data("window")
        
        # exports
        core.SharedData.export_data("camera", self)
        return

    # setup basic settings (window, gui, logs etc)
    def init(self):                
        return

    # executed every frame
    def update(self):
        # update aspect in case window resized -> change to on dirty callback
        self.aspect = self.wnd.width / self.wnd.height
        
        # update matrices
        self.view = self.look_at()
        self.projection = self.perspective()

        return

    # reset any modified parameters or files
    def reset(self):
        # eye, at, up vector (lookAt)
        self.eye = np.array([5.0, 5.0, 5.0], dtype=np.float32) # position
        self.at = np.array([0.0, 0.0, 0.0], dtype=np.float32) # target
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32) # up direction
        self.view = self.look_at()
        
        # projection parameters
        self.fovy = np.radians(60.0)
        self.aspect = self.wnd.width / self.wnd.height if self.wnd is not None else 16.0 / 9.0
        self.near = 0.1
        self.far = 100.0
        self.projection = self.perspective()
        
        return

    # release runtime data
    def release(self):
        return