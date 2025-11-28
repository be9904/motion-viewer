import numpy as np
from OpenGL.GL import *

import core
from core.glwrapper import GLWrapper as glw
from core.mesh import Sphere
from plugins.light import Light

class Test(core.Plugin):
    def __init__(self):
        super().__init__()
        
        self.sphere = None
        self.light = Light() # plugins should be instantiated in __init__()
    
    def assemble(self):
        self.shader = core.SharedData.import_shader("std_shader")
    
    def init(self):        
        # Sun (root object)
        self.sphere = core.Object(
            name="Sun",
            position=(0, 0, 0),
            rotation=(0, 0, 0),
            scale=(2, 2, 2)
        )
        self.sphere.add_component("mesh", Sphere(lat=32, lon=32))
        glw.set_instance_uniform(
            self.shader.program,
            self.sphere.components["mesh"].vao,
            self.sphere.components["mesh"].model,
            len(self.sphere.components["mesh"].indices)
        )
        
        print(f"  Sphere has {len(self.sphere.children)} children")
    
    def update(self):
        if not self.shader or not self.sphere:
            print(f"Corrupt initialization. Check {'shader' if not self.shader else ''}")
            return
    
    def reset(self):
        return
    
    def release(self):
        return

