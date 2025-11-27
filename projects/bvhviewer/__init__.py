import core
import numpy as np
from OpenGL.GL import *

# Import your specific plugins
from plugins.animator import Animator
from core.mesh import Cube

class BVHViewer(core.Plugin):
    def __init__(self):
        super().__init__()
        self.animator = None
        self.camera = None
        self.floor = None
        self.shader = None

    def assemble(self):
        # 1. Get Camera from SharedData
        # We assume the Camera plugin has already been assembled (exported) by main.py
        self.camera = core.SharedData.import_data("camera")
        
        if self.camera:
            # 2. Configure Camera specifically for this Scene
            # Override default camera position to see the skeleton
            self.camera.eye = np.array([0.0, 20.0, 100.0], dtype=np.float32)
            self.camera.at = np.array([0.0, 10.0, 0.0], dtype=np.float32)
            
            # Force a matrix update so 'view' and 'projection' are valid immediately
            if hasattr(self.camera, 'update'):
                self.camera.update()
        else:
            print("BVHViewer Warning: No 'camera' found in SharedData. Ensure Camera plugin is assembled first.")

        # 3. Setup Shader
        try:
            self.shader = core.Shader("assets/shaders/vertex.glsl", "assets/shaders/fragment.glsl")
            core.SharedData.export_data("standard_shader", self.shader)
        except Exception as e:
            print(f"Project Error: Could not load shaders. {e}")

    def init(self):
        # 1. Initialize Animator
        self.animator = Animator()
        self.animator.init()
        
        # 2. Create Floor
        self.floor = core.Object("Floor", position=(0, 0, 0), scale=(50, 0.1, 50))
        self.floor.add_component("mesh", Cube())
        
        print("BVHViewer: Initialized.")

    def update(self):
        # 1. Update Camera
        # Since we are sharing the camera, we ensure it updates its matrices
        if self.camera:
            self.camera.update()

        # 2. Update Animator
        if self.animator:
            self.animator.update()

        # 3. Draw Floor
        if self.shader and self.floor:
            glUseProgram(self.shader.program)
            
            if self.camera:
                self.shader.set_uniform_matrix4fv("view_matrix", self.camera.view)
                self.shader.set_uniform_matrix4fv("projection_matrix", self.camera.projection)
            
            self.floor.draw(self.shader.program)

    def release(self):
        if self.animator:
            self.animator.release()
        # Note: We do not release self.camera because we do not own it (it's shared)
        self.floor = None