import core
from core.mesh import *

class Hello(core.Plugin):
    def __init__(self):
        self.cube = Cube(size=2)
    
    # assemble all configurations and files
    def assemble(self):
        return

    # setup basic settings (window, gui, logs etc)
    def init(self):
        # enable depth and lighting once
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 5, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        return

    # executed every frame
    def update(self):
        glColor3f(0.8, 0.2, 0.2)
        self.cube.draw()
        return

    # reset any modified parameters or files
    def reset(self):
        return

    # release runtime data
    def release(self):
        return
