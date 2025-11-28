"""
Solar System Demo - Demonstrates Object hierarchy with parent-child transforms
"""
import numpy as np
import core
from core.mesh import Sphere
from OpenGL.GL import *
from core.glwrapper import GLWrapper as glw

class Test(core.Plugin):
    def __init__(self):
        self.sun = None
        self.shader = None
        self.camera = None
        self.time = 0
    
    def assemble(self):
        """Import shared resources"""
        self.camera = core.SharedData.import_data("camera")
        self.shader = core.SharedData.import_shader("std_shader")
        return
    
    def init(self):
        """Create solar system hierarchy"""
        
        # Sun (root object)
        self.sun = core.Object(
            name="Sun",
            position=(0, 0, 0),
            rotation=(0, 0, 0),
            scale=(2, 2, 2)
        )
        sun_mesh = Sphere(lat=32, lon=32)
        self.sun.add_component("mesh", sun_mesh)
        glw.set_uniform(self.shader.program, self.sun.components["mesh"].model, "model_matrix")
        
        print("Solar System created!")
        print(f"  Sun has {len(self.sun.children)} children")
        print(f"  Earth has {len(self.earth.children)} children")
        
        return
    
    def update(self):
        """Animate the solar system"""
        if not self.shader or not self.camera or not self.sun:
            return
        
        # Increment time
        self.time += 0.01
        
        # Animate celestial bodies
        # Sun rotates on its axis
        self.sun.set_rotation_euler((0, self.time * 20, 0))
        
        # Earth orbits around Sun (inherited from sun's rotation)
        # AND rotates on its own axis
        self.earth.set_rotation_euler((0, self.time * 50, 23.5))
        
        # Moon orbits around Earth (inherited from earth's rotation)
        # AND rotates on its own axis
        self.moon.set_rotation_euler((0, self.time * 80, 5))
        
        # Mars orbits slower
        self.mars.set_rotation_euler((0, self.time * 30, 0))
        
        # Render
        glUseProgram(self.shader.program)
        
        # Set camera matrices once
        self.shader.set_uniform_matrix4fv("view_matrix", self.camera.view)
        self.shader.set_uniform_matrix4fv("projection_matrix", self.camera.projection)
        
        # Draw entire hierarchy with one call
        # This automatically:
        # 1. Draws Sun with its world matrix
        # 2. Draws Earth with Sun's transform * Earth's transform
        # 3. Draws Moon with Sun's * Earth's * Moon's transform
        # 4. Draws Mars with Sun's * Mars's transform
        self.sun.draw(self.shader.program)
        
        return
    
    def reset(self):
        self.time = 0
        return
    
    def release(self):
        return

