import numpy as np
from OpenGL.GL import *

class Mesh:
    def __init__(self, size=1.0):
        pass

class Cube:
    def __init__(self, size=1.0):
        self.size = size
        self.vertices = np.array([
            [-1, -1, -1],
            [ 1, -1, -1],
            [ 1,  1, -1],
            [-1,  1, -1],
            [-1, -1,  1],
            [ 1, -1,  1],
            [ 1,  1,  1],
            [-1,  1,  1],
        ], dtype=np.float32) * size / 2

        self.faces = [
            [0, 1, 2, 3],  # back
            [4, 5, 6, 7],  # front
            [0, 1, 5, 4],  # bottom
            [2, 3, 7, 6],  # top
            [0, 3, 7, 4],  # left
            [1, 2, 6, 5],  # right
        ]

        self.colors = [
            [1,0,0], [0,1,0], [0,0,1],
            [1,1,0], [1,0,1], [0,1,1]
        ]

    def draw(self):
        glBegin(GL_QUADS)
        for i, face in enumerate(self.faces):
            glColor3fv(self.colors[i])
            # compute normal for basic lighting
            v0, v1, v2 = self.vertices[face[0]], self.vertices[face[1]], self.vertices[face[2]]
            normal = np.cross(v1 - v0, v2 - v0)
            normal = normal / np.linalg.norm(normal)
            glNormal3fv(normal)
            for vertex_idx in face:
                glVertex3fv(self.vertices[vertex_idx])
        glEnd()
