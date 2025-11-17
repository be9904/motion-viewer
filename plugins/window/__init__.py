import glfw
from OpenGL.GL import *
from core import *
from .config import *
from .keyboard import *

class Window(Plugin):
    def __init__(self):
        # super().__init__()
        self.window = None
        self.width = WIDTH
        self.height = HEIGHT

    # assemble all configurations and files
    def assemble(self):
        # add ui

        # set keyboard callbacks
        glfw.set_key_callback(self.window, key_callback)
        
        return

    # setup basic settings (window, gui, logs etc)
    def init(self):
        # init GLFW
        if not glfw.init():
            raise Exception(f"{init.__name__}(): failed in glfw.init()")

        # create window
        window = glfw.create_window(WIDTH, HEIGHT, TITLE, None, None)

        if not window:
            glfw.terminate()
            raise Exception("Failed to create GLFW window")

        # make the OpenGL context current
        glfw.make_context_current(window)
        
        self.window = window

    # executed every frame
    def update(self):
        glfw.poll_events()

        # set clear color & clear the screen
        glClearColor(*BG_COLOR)
        glClear(GL_COLOR_BUFFER_BIT)

        # swap front and back buffers
        glfw.swap_buffers(self.window)

    # reset any modified parameters or files
    def reset(self):
        return

    # release runtime data
    def release(self):
        if not self.window:
            return
        
        glfw.destroy_window(self.window)
        glfw.terminate()

        return