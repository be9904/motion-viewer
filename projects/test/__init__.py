import numpy as np
from OpenGL.GL import *

import core
from core.glwrapper import GLWrapper as glw
from core.mesh import Sphere
from plugins.light import Light

class Test(core.Plugin):
    def __init__(self):
        super().__init__()
        
        self.sun = core.Object("sun",scale=(2,2,2))
        self.light = Light()
    
    def assemble(self):
        print("Test.assemble()")
        self.shader = core.SharedData.import_shader("std_shader")
    
    def init(self):        
        print("Test.init()")
        # Sun (root object)
        self.sun.mesh = Sphere(lat=32, lon=32)
        self.sun.shader = self.shader
        self.sun.init()

        # light
        # self.light = 
        
        print(f"sun has {len(self.sun.children)} children")
    
    def update(self):
        if not self.shader or not self.sun:
            print(f"Corrupt initialization. Check {'shader' if not self.shader else ''}")
            return

        self.sun.update()
        # self.sun.draw()
    
    def reset(self):
        return
    
    def release(self):
        return

