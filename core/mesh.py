import numpy as np
from OpenGL.GL import *
import quaternion as qt

class Mesh:
    def __init__(self, size=1.0):
        # vertices & indices
        self.vertices = np.zeros((0, 3), dtype=np.float32)
        self.indices = np.zeros((0,), dtype=np.uint32)
        
        # buffers
        self.vao = None
        self.vbo = None
        self.ebo = None
    
    def upload(self):
        # safety check
        if not isinstance(self.vertices, np.ndarray):
            raise TypeError("vertices must be a numpy array")
        if not isinstance(self.indices, np.ndarray):
            raise TypeError("indices must be a numpy array")
    
        # build VAO + VBOs
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # vertex VBO
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # index buffer
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # layout: location=0 → vertex position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        # glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, None)

        glBindVertexArray(0)

class Cube:
    def __init__(self, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=1.0):
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.scale = np.float32(scale)

        self.quaternion = qt.from_euler_angles(
            np.radians(self.rotation[0]),
            np.radians(self.rotation[1]),
            np.radians(self.rotation[2]),
        )

        # 8 cube vertices in model space (scaled)
        self.vertices = (
            np.array(
                [
                    [-1, -1, -1],
                    [1, -1, -1],
                    [1, 1, -1],
                    [-1, 1, -1],
                    [-1, -1, 1],
                    [1, -1, 1],
                    [1, 1, 1],
                    [-1, 1, 1],
                ],
                dtype=np.float32,
            ) * self.scale / 2.0
        )

        # triangle index buffer (two triangles per face)
        self.indices = np.array(
            [
                0,1,2, 0,2,3,  # back
                4,5,6, 4,6,7,  # front
                0,1,5, 0,5,4,  # bottom
                2,3,7, 2,7,6,  # top
                0,3,7, 0,7,4,  # left
                1,2,6, 1,6,5,  # right
            ], dtype=np.uint32
        )
        
        self.upload()
