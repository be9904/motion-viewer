import numpy as np
from OpenGL.GL import *

def draw_triangle():
    # Define vertices: e.g., in normalized device coordinates (‑1..1)
    vertices = np.array([
        [ 0.0,  0.5, 0.0],  # top
        [-0.5, -0.5, 0.0],  # bottom left
        [ 0.5, -0.5, 0.0],  # bottom right
    ], dtype=np.float32)

    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, vertices)
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glDisableClientState(GL_VERTEX_ARRAY)