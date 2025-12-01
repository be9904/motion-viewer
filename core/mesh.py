import numpy as np
from OpenGL.GL import *
import quaternion as qt

import core
from core.glwrapper import GLWrapper as glw

class Mesh:
    def __init__(self, size=1.0):
        # vertices & indices
        self.vertices = np.zeros((0, 3), dtype=np.float32)
        self.indices = np.zeros((0,), dtype=np.uint32)
        self.normals = np.zeros((0, 3), dtype=np.float32)
        
        # buffers
        self.vao = None # vertex array
        self.vbo = None # vertex buffer
        self.ebo = None # index buffer

        print("WARNING: This class should not be instantiated. Use a child class or define a child class of this class.")

    def update_buffers(self):
        # safety check
        if not isinstance(self.vertices, np.ndarray):
            raise TypeError("vertices must be a numpy array")
        if not isinstance(self.indices, np.ndarray):
            raise TypeError("indices must be a numpy array")
    
        # build VAO (bind later)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # vertex VBO
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0) # location 0 in shader
        # for floats, always use GL_FALSE
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None) # bind position to location 0
        
        # normal VBO
        self.nbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.nbo)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1) # location 1 in shader
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None) # bind normals to location 1

        # index buffer
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # unbind vao at end
        glBindVertexArray(0)

class Sphere(Mesh):
    def __init__(self, lat=64, lon=64):
        # self.position = np.array(position, dtype=np.float32)
        # self.rotation = np.array(rotation, dtype=np.float32)
        # self.scale = np.array(scale, dtype=np.float32)

        # self.quaternion = qt.from_euler_angles(
        #     np.radians(self.rotation[0]),
        #     np.radians(self.rotation[1]),
        #     np.radians(self.rotation[2]),
        # )

        # # model matrix
        # self.model = core.get_model_matrix(self.position, self.quaternion, self.scale)

        # tesselation
        self.lat = lat
        self.lon = lon

        # buffers
        self.vertices = None
        self.normals = None
        self.indices = None

        # init buffers
        self.create_buffers()
        self.update_buffers()
        
    # called with object instantiation
    def create_buffers(self):
        vertices = []
        normals = []
        indices = []
        
        # vertex & normals
        for i in range(self.lat + 1):
            theta = i * np.pi / self.lat
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)
            
            for j in range(self.lon + 1):
                phi = j * 2 * np.pi / self.lon
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)

                x = cos_phi * sin_theta
                y = cos_theta
                z = sin_phi * sin_theta

                vertices.append([x, y, z])
                normals.append([x, y, z])
                
        # indices
        for i in range(self.lat):
            for j in range(self.lon):
                first = i * (self.lon + 1) + j
                second = first + self.lon + 1

                indices.extend([first, second, first + 1])
                indices.extend([second, second + 1, first + 1])
                
        self.vertices = np.array(vertices, dtype=np.float32)
        self.normals = np.array(normals, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.uint32)
        return
    
    # only when vertex info changes, shouldn't be called
    def update_buffers(self):
        super().update_buffers()

    # call when updating tesselation
    def update_tesselation(self, lat, lon):
        self.lat = lat
        self.lon = lon

        self.create_buffers()
        self.update_buffers()

        return

    # inject into update loop
    def draw(self, program=None):
        # bind vao
        if self.vao is not None:
            glBindVertexArray(self.vao)
            
        if program is None:
            raise ValueError("Program is not specified.")

        # notify which program to use
        glUseProgram(program)

        # draw every frame
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        return
        
class Cube(Mesh):
    def __init__(self):
        # self.position = np.array(position, dtype=np.float32)
        # self.rotation = np.array(rotation, dtype=np.float32)
        # self.scale = np.array(scale, dtype=np.float32)

        # self.quaternion = qt.from_euler_angles(
        #     np.radians(self.rotation[0]),
        #     np.radians(self.rotation[1]),
        #     np.radians(self.rotation[2]),
        # )

        # # model matrix
        # self.model = core.get_model_matrix(self.position, self.quaternion, self.scale)

        # buffers
        self.vertices = None
        self.normals = None
        self.indices = None     

        # init buffers
        self.create_buffers()
        self.update_buffers()   

    # called with object instantiation
    def create_buffers(self):
        vertices = np.array([
            [-1, -1,  1], [ 1, -1,  1], [ 1,  1,  1], [-1,  1,  1], # Front face (+Z)
            [ 1, -1, -1], [-1, -1, -1], [-1,  1, -1], [ 1,  1, -1], # Back face (-Z)
            [-1, -1, -1], [-1, -1,  1], [-1,  1,  1], [-1,  1, -1], # Left face (-X)
            [ 1, -1,  1], [ 1, -1, -1], [ 1,  1, -1], [ 1,  1,  1], # Right face (+X)
            [-1,  1,  1], [ 1,  1,  1], [ 1,  1, -1], [-1,  1, -1], # Top face (+Y)
            [-1, -1, -1], [ 1, -1, -1], [ 1, -1,  1], [-1, -1,  1], # Bottom face (-Y)
        ], dtype=np.float32)

        # Normals: 1 per vertex, pointing out of the face
        normals = np.array([
            [0, 0,  1], [0, 0,  1], [0, 0,  1], [0, 0,  1], # Front
            [0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1], # Back
            [-1, 0, 0], [-1, 0, 0], [-1, 0, 0], [-1, 0, 0], # Left
            [ 1, 0, 0], [ 1, 0, 0], [ 1, 0, 0], [ 1, 0, 0], # Right
            [0,  1, 0], [0,  1, 0], [0,  1, 0], [0,  1, 0], # Top
            [0, -1, 0], [0, -1, 0], [0, -1, 0], [0, -1, 0], # Bottom
        ], dtype=np.float32)

        # Indices (two triangles per face)
        indices = np.array([
            0,1,2, 0,2,3,       # Front
            4,5,6, 4,6,7,       # Back
            8,9,10, 8,10,11,    # Left
            12,13,14, 12,14,15, # Right
            16,17,18, 16,18,19, # Top
            20,21,22, 20,22,23, # Bottom
        ], dtype=np.uint32)

        self.vertices = vertices
        self.normals = normals
        self.indices = indices
        return

    # only when vertex info changes, shouldn't be called
    def update_buffers(self):
        super().update_buffers()

    # inject into update loop
    def draw(self, program=None):
        # bind vao
        if self.vao is not None:
            glBindVertexArray(self.vao)
            
        if program is None:
            raise ValueError("Program is not specified.")

        # notify which program to use
        glUseProgram(program)

        # draw every frame
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        return