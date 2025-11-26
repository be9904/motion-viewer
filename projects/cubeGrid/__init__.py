"""
Cube Grid Demo - Multiple independent objects using Object system
"""
import numpy as np
import core
from core.mesh import Cube, Sphere
from OpenGL.GL import *

class CubeGrid(core.Plugin):
    def __init__(self):
        self.objects = []
        self.shader = None
        self.camera = None
        self.time = 0
    
    def assemble(self):
        """Import shared resources"""
        self.camera = core.SharedData.import_data("camera")
        self.shader = core.SharedData.import_data("standard_shader")
        return
    
    def init(self):
        """Create grid of cubes"""
        
        # Create 5x5 grid of cubes
        for x in range(-2, 3):
            for z in range(-2, 3):
                # Create object with transform
                obj = core.Object(
                    name=f"Cube_{x}_{z}",
                    position=(x * 2.5, 0, z * 2.5),
                    rotation=(0, 0, 0),
                    scale=(0.5, 0.5, 0.5)
                )
                
                # Add mesh component
                if (x + z) % 2 == 0:
                    mesh = Cube()
                else:
                    mesh = Sphere(lat=16, lon=16)
                
                obj.add_component("mesh", mesh)
                self.objects.append(obj)
        
        print(f"Created {len(self.objects)} objects in grid")
        return
    
    def update(self):
        """Draw all objects"""
        if not self.shader or not self.camera:
            return
        
        self.time += 0.01
        
        # Animate objects - each has independent movement
        for i, obj in enumerate(self.objects):
            # Wave effect based on position
            offset = i * 0.3
            y = np.sin(self.time + offset) * 0.5
            
            # Update position (keep x, z the same)
            pos = obj.transform.position
            obj.set_position((pos[0], y, pos[2]))
            
            # Rotate each object
            obj.rotate_euler((0.5, 1, 0))
        
        # Render
        glUseProgram(self.shader.program)
        
        # Set camera matrices
        self.shader.set_uniform_matrix4fv("view_matrix", self.camera.view)
        self.shader.set_uniform_matrix4fv("projection_matrix", self.camera.projection)
        
        # Draw all objects
        for obj in self.objects:
            obj.draw(self.shader.program)
        
        return
    
    def reset(self):
        self.time = 0
        return
    
    def release(self):
        return

