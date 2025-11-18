# library imports
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import glfw

# local imports
import core
from .config import *

class Camera(core.Plugin):
    def __init__(self, window=None):
        # reference to program window
        self.wnd = window
        
        # camera position, rotation (Euler angles -> pitch, yaw, roll), up vector and target (lookAt)
        self.position = np.array([0.0, 0.0, 5.0], dtype=np.float32)
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
        
        # mouse / input state
        self.last_mouse = None
        self.left_dragging = False
        self.right_dragging = False

        # control sensitivity
        self.pan_sensitivity = 0.005
        self.orbit_sensitivity = 0.2
        self.zoom_sensitivity = 0.5
        self.move_speed = 0.1
    
    # assemble all configurations and files
    def assemble(self):
        # export to shared data
        core.SharedData.export_data("camera", self)
        return

    # setup basic settings (window, gui, logs etc)
    def init(self):
        # enable depth test
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # register glfw callbacks
        if not self.wnd:
            raise Exception(f"{self.__class__.__name__}.init(): missing window reference")
        glfw.set_key_callback(self.wnd.window, self.keyboard)
        glfw.set_cursor_pos_callback(self.wnd.window, self.mouse_motion)
        glfw.set_mouse_button_callback(self.wnd.window, self.mouse_button)
        glfw.set_scroll_callback(self.wnd.window, self.mouse_scroll)
        
        # print control hints to console
        self.control_hint()
        
        return

    # executed every frame
    def update(self):
        # update aspect in case window resized -> change to on dirty callback
        self.aspect = self.wnd.width / self.wnd.height

        return

    # reset any modified parameters or files
    def reset(self):
        # reset position, rotation, up vector and target
        self.position[:] = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.rotation[:] = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.up[:] = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.target[:] = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.last_mouse = None
        
        return

    # release runtime data
    def release(self):
        return
    
    ##############################################
    # Trackball & Movement
    ##############################################

    # move camera
    def move(self, direction):
        forward = core.normalize(self.target - self.position)
        right = core.normalize(np.cross(self.up, forward))
        up = self.up

        world = (
            right * direction[0] +
            up * direction[1] +
            forward * direction[2]
        )

        self.position += world
        self.target += world

    # rotate camera in place (Euler angles)
    def rotate(self, pitch=0, yaw=0, roll=0):
        self.rotation += np.array([pitch, yaw, roll], dtype=np.float32)

    # zoom camera toward target
    def zoom(self, amount):
        forward = core.normalize(self.target - self.position)
        self.position += forward * amount

    # pan camera perpendicular to view direction
    def pan(self, dx=0, dy=0):
        forward = core.normalize(self.target - self.position)
        right = core.normalize(np.cross(self.up, forward))
        up = core.normalize(np.cross(forward, right))
        self.position += right * dx + up * dy
        self.target += right * dx + up * dy

    # orbit camera around the target point
    def orbit(self, yaw=0, pitch=0):
        yaw_rad = np.radians(yaw)
        pitch_rad = np.radians(pitch)

        direction = self.position - self.target
        r = np.linalg.norm(direction)
        theta = np.arctan2(direction[2], direction[0]) + yaw_rad
        phi = np.arccos(direction[1] / r) + pitch_rad

        # clamp phi to avoid flipping over poles
        phi = np.clip(phi, 0.01, np.pi - 0.01)

        # convert spherical coordinates back to Cartesian
        self.position[0] = r * np.sin(phi) * np.cos(theta) + self.target[0]
        self.position[1] = r * np.cos(phi) + self.target[1]
        self.position[2] = r * np.sin(phi) * np.sin(theta) + self.target[2]
        
    ##############################################
    # Input Handlers
    ##############################################
    
    def control_hint(self):
        print("W: Forward")
        print("A: Left")
        print("S: Backward")
        print("D: Right")
        print("Q: Down")
        print("E: Up")
        print("Arrow Keys: Orbit around Target")
        print("LMB: Orbit")
        print("RMB: Pan")
        print("Scroll: Zoom")

    def keyboard(self, window, key, scancode, action, mods):
        if action not in [glfw.PRESS, glfw.REPEAT]:
            return
        
        # WASD+QE movement
        if key == glfw.KEY_W:   self.move([0, 0, self.move_speed])
        elif key == glfw.KEY_S: self.move([0, 0, -self.move_speed])
        elif key == glfw.KEY_A: self.move([self.move_speed, 0, 0])
        elif key == glfw.KEY_D: self.move([-self.move_speed, 0, 0])
        elif key == glfw.KEY_Q: self.move([0, -self.move_speed, 0])
        elif key == glfw.KEY_E: self.move([0, self.move_speed, 0])
        
        # arrow keys for orbit
        elif key == glfw.KEY_LEFT:  self.orbit(yaw=-self.orbit_sensitivity)
        elif key == glfw.KEY_RIGHT: self.orbit(yaw=self.orbit_sensitivity)
        elif key == glfw.KEY_UP:    self.orbit(pitch=self.orbit_sensitivity)
        elif key == glfw.KEY_DOWN:  self.orbit(pitch=-self.orbit_sensitivity)

    def mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT:
            self.left_dragging = (action == glfw.PRESS)
        elif button == glfw.MOUSE_BUTTON_RIGHT:
            self.right_dragging = (action == glfw.PRESS)
            
        self.last_mouse = glfw.get_cursor_pos(window)

    def mouse_motion(self, window, xpos, ypos):
        if self.last_mouse is None:
            self.last_mouse = (xpos, ypos)
            return

        dx = xpos - self.last_mouse[0]
        dy = ypos - self.last_mouse[1]

        if self.left_dragging:
            self.orbit(yaw=dx * self.orbit_sensitivity, pitch=-dy * self.orbit_sensitivity)
        elif self.right_dragging:
            self.pan(dx * self.pan_sensitivity, dy * self.pan_sensitivity)

        self.last_mouse = (xpos, ypos)

    def mouse_scroll(self, window, xoffset, yoffset):
        self.zoom(yoffset * self.zoom_sensitivity)