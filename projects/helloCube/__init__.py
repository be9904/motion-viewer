import ctypes

import numpy as np

import core
from core.mesh import *

class HelloCube(core.Plugin):
    def __init__(self):
        self.cube = Cube(position=(0,1,0),rotation=(0,0,0),scale=(1,1,1))
        self.camera = None
        self.shader = core.Shader("shaders/cel/cel.vert", "shaders/cel/cel.frag")
        self.axis_vao = None
        self.axis_vbo = None
        self.axis_length = 100.0
        self.axis_vertex_count = 0
        self.identity_matrix = np.eye(4, dtype=np.float32)
        
        # class member matrices
        self.model_matrix = core.get_model_matrix(self.cube.position, self.cube.quaternion, self.cube.scale)
        self.view_matrix = None
        self.projection_matrix = None
    
    # assemble all configurations and files
    def assemble(self):
        self.camera = core.SharedData.import_data("camera")
        return

    # setup basic settings (window, gui, logs etc)
    def init(self):
        # draw axes
        self._init_axes()

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
        
        # draw world axes
        self._draw_axes()

    # reset any modified parameters or files
    def reset(self):
        return

    # release runtime data
    def release(self):
        return

    def _init_axes(self):
        if self.axis_vao:
            return
        
        axis = self.axis_length
        # position (xyz) + normal (xyz) per vertex
        axis_vertices = np.array([
            # X axis
            -axis, 0.0, 0.0, 1.0, 0.0, 0.0,
             axis, 0.0, 0.0, 1.0, 0.0, 0.0,
            # Y axis
            0.0, -axis, 0.0, 0.0, 1.0, 0.0,
            0.0,  axis, 0.0, 0.0, 1.0, 0.0,
            # Z axis
            0.0, 0.0, -axis, 0.0, 0.0, 1.0,
            0.0, 0.0,  axis, 0.0, 0.0, 1.0,
        ], dtype=np.float32)
        
        self.axis_vertex_count = len(axis_vertices) // 6
        
        self.axis_vao = glGenVertexArrays(1)
        self.axis_vbo = glGenBuffers(1)
        
        glBindVertexArray(self.axis_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.axis_vbo)
        glBufferData(GL_ARRAY_BUFFER, axis_vertices.nbytes, axis_vertices, GL_STATIC_DRAW)
        
        stride = 6 * axis_vertices.itemsize
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def _draw_axes(self):
        if not self.axis_vao or not self.camera:
            return
        
        # use identity model matrix so axes stay in world space
        self.shader.set_uniform_matrix4fv("model", self.identity_matrix)
        
        glBindVertexArray(self.axis_vao)
        
        axis_configs = [
            ((1.0, 0.0, 0.0, 1.0), 0),  # X axis - red
            ((0.0, 1.0, 0.0, 1.0), 2),  # Y axis - green
            ((0.0, 0.0, 1.0, 1.0), 4),  # Z axis - blue
        ]
        
        for color, start in axis_configs:
            self.shader.set_uniform_vec4("objectColor", color)
            glDrawArrays(GL_LINES, start, 2)
        
        glBindVertexArray(0)
        
        # restore object color for cube rendering in next frame
        self.shader.set_uniform_vec4("objectColor", (1.0, 0.5, 0.31, 1.0))
