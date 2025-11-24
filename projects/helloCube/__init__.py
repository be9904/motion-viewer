import ctypes

import numpy as np

import core
from core.mesh import *
from core.curve import *

class HelloCube(core.Plugin):
    def __init__(self):
        self.camera = None
        self.cube = None
        self.shader = None
        self.identity_matrix = np.eye(4, dtype=np.float32)
        
        # class member matrices
        self.model_matrix = None
        self.view_matrix = None
        self.projection_matrix = None
    
    # assemble all configurations and files
    def assemble(self):
        self.camera = core.SharedData.import_data("camera")
        return

    # setup basic settings (window, gui, logs etc)
    def init(self):
        self.cube = Sphere(position=(0,1,0),rotation=(0,0,0),scale=(1,1,1))
        self.shader = core.SharedData.import_data("shader")

        # TODO: setup model matrix
        self.model_matrix = core.get_model_matrix(self.cube.position, self.cube.quaternion, self.cube.scale)
        
        # TODO: setup view & projection matrix
        if self.camera:
            self.view_matrix = core.get_view_matrix(self.camera)
            self.projection_matrix = core.get_projection_matrix(self.camera)
        return

    # executed every frame
    def update(self):
        if not self.camera or not self.cube:
            return
        
        glUseProgram(self.shader.program)
        
        # update matrices
        self.model_matrix = core.get_model_matrix(self.cube.position,
                                                self.cube.quaternion,
                                                self.cube.scale)
        self.view_matrix = core.get_view_matrix(self.camera)
        self.projection_matrix = core.get_projection_matrix(self.camera)

        # set uniforms using your helper
        self.shader.set_uniform_matrix4fv("model", self.model_matrix)
        self.shader.set_uniform_matrix4fv("view", self.view_matrix)
        self.shader.set_uniform_matrix4fv("projection", self.projection_matrix)
        
        # set lighting
        self.shader.set_uniform_vec4("lightPos", (5.0, 5.0, 5.0, 0.0))
        self.shader.set_uniform_vec4("lightColor", (1.0, 1.0, 1.0, 1.0))
        self.shader.set_uniform_vec4("objectColor", (1.0, 0.5, 0.31, 1.0))
        
        # bind cube VAO and draw
        glBindVertexArray(self.cube.vao)
        glDrawElements(GL_TRIANGLES, len(self.cube.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0) # unbind vao

    # reset any modified parameters or files
    def reset(self):
        return

    # release runtime data
    def release(self):
        return