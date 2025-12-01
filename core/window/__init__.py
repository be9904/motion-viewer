import glfw
from OpenGL.GL import *
from core import *
from .config import *
from .keyboard import *

class Window(Plugin):
    def __init__(self):
        # special plugin where callbacks are handled manually
        # super().__init__() 
        
        self.glfw_window = None
        self.width = WIDTH
        self.height = HEIGHT
        
        # init GLFW
        if not glfw.init():
            raise Exception(f"{self.__class__.__name__}.init(): failed in glfw.init()")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)  # Required on macOS
        
        # create window
        self.glfw_window = glfw.create_window(WIDTH, HEIGHT, TITLE, None, None)

        if not self.glfw_window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")
        
        # make the OpenGL context current
        glfw.make_context_current(self.glfw_window)
        
        # export window object
        SharedData.export_data("window", self)

    # assemble all configurations and files
    def assemble(self):
        # add ui

        # set keyboard callbacks
        glfw.set_key_callback(self.glfw_window, key_callback)
        
        return

    # setup basic settings (window, gui, logs etc)
    def init(self):
        glClearColor(*BG_COLOR)
        return

    # executed every frame
    def update(self):
        glfw.poll_events()

        # clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # executed after drawing elements
    def post_update(self):
        # swap front and back buffers
        glfw.swap_buffers(self.glfw_window)
        
        return

    # reset any modified parameters or files
    def reset(self):
        return

    # release runtime data
    def release(self):
        if not self.glfw_window:
            return
        
        glfw.destroy_window(self.glfw_window)
        glfw.terminate()

        return