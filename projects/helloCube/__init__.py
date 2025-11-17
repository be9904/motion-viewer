import core
from core.mesh import *

class HelloCube(core.Plugin):
    def __init__(self):
        self.cube = Cube(position=(0,0,0),rotation=(0,0,0),scale=(1,1,1))
        self.camera = None
        # enable depth and lighting once
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 5, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # assemble all configurations and files
    def assemble(self):
        self.camera = core.SharedData.import_data("camera")
        core.SharedData.set_callback("camera", self.update)
        return

    # setup basic settings (window, gui, logs etc)
    def init(self):
        self.MVP = core.get_mvp_matrix(self.cube.position, self.cube.quaternion, self.cube.scale, self.camera)
        return

    # executed every frame
    def update(self):
        return

    # reset any modified parameters or files
    def reset(self):
        return

    # release runtime data
    def release(self):
        return
