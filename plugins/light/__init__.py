from OpenGL.GL import *

import core
from core.glwrapper import GLWrapper as glw

class Light(core.Plugin):
    def __init__(self, position=(1.0, -5.0, 1.0, 0.0)):
        super().__init__()
        
        self.transform = core.Transform(position=position)
        self.color = (1,1,1)
        self.intensity = 1.0
        
        self.shader = None
    
    # assemble all configurations and files
    def assemble(self):
        # imports
        self.shader = core.SharedData.import_shader("std_shader")
        
        # exports

        return

    # setup basic settings before update loop
    def init(self):
        # init uniforms
        glw.set_uniform(self.shader.program, self.transform.position,   "light_position")
        glw.set_uniform(self.shader.program, self.color,                "light_color")
        glw.set_uniform(self.shader.program, self.intensity,            "light_intensity")
        return

    # executed every frame
    def update(self):
        self.transform.update()
        return

    # reset any modified parameters or files
    def reset(self):
        # self.position = (1.0, -1.0, 1.0, 0.0)
        return

    # release runtime data
    def release(self):
        # self.position = None
        return
