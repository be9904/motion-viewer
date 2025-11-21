import numpy as np
from OpenGL.GL import *
import quaternion as qt

class Mesh:
    def __init__(self, size=1.0):
        # vertices & indices
        self.vertices = np.zeros((0, 3), dtype=np.float32)
        self.indices = np.zeros((0,), dtype=np.uint32)
        self.normals = np.zeros((0, 3), dtype=np.float32)
        
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
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        
        # normal VBO
        self.nbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.nbo)
        glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        # index buffer
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        # layout: location=0 → vertex position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        # glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, None)

        glBindVertexArray(0)

class Sphere(Mesh):
    def __init__(self, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(1.0,1.0,1.0), lat=64, lon=64):
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.scale = np.array(scale, dtype=np.float32)

        self.quaternion = qt.from_euler_angles(
            np.radians(self.rotation[0]),
            np.radians(self.rotation[1]),
            np.radians(self.rotation[2]),
        )

        vertices = []
        normals = []
        indices = []
        
        # vertex & normals
        for i in range(lat + 1):
            theta = i * np.pi / lat
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)
            
            for j in range(lon + 1):
                phi = j * 2 * np.pi / lon
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)

                x = cos_phi * sin_theta
                y = cos_theta
                z = sin_phi * sin_theta

                vertices.append([x, y, z])
                normals.append([x, y, z])
                
        # indices
        for i in range(lat):
            for j in range(lon):
                first = i * (lon + 1) + j
                second = first + lon + 1

                indices.extend([first, second, first + 1])
                indices.extend([second, second + 1, first + 1])
                
        self.vertices = np.array(vertices, dtype=np.float32) * self.scale
        self.normals = np.array(normals, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.uint32)

    def upload(self):
        super().upload()
        
class Cube(Mesh):
    def __init__(self, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(1.0,1.0,1.0)):
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.scale = np.array(scale, dtype=np.float32)

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
                0,2,1, 0,3,2,  # back
                4,5,6, 4,6,7,  # front
                0,1,5, 0,5,4,  # bottom
                2,3,7, 2,7,6,  # top
                0,7,3, 0,4,7,  # left
                1,2,6, 1,6,5,  # right
            ], dtype=np.uint32
        )
        
        # normals per vertex (face normals, not normalized - will be normalized in shader if needed)
        # Each vertex belongs to 3 faces, so we use the average normal
        # For simplicity, using face normals: each vertex gets the normal of its primary face
        self.normals = np.array([
            [-1,-1,-1],
            [1,-1,-1],
            [1,1,-1],
            [-1,1,-1],
            [-1,-1,1],
            [1,-1,1],
            [1,1,1],
            [-1,1,1],
        ], dtype=np.float32)
        
        # Actually, let's compute proper per-vertex normals by averaging face normals
        # Each vertex is shared by 3 faces
        face_normals = {
            # back face (z = -1)
            (0,2,1): [0, 0, -1], (0,3,2): [0, 0, -1],
            # front face (z = 1)  
            (4,5,6): [0, 0, 1], (4,6,7): [0, 0, 1],
            # bottom face (y = -1)
            (0,1,5): [0, -1, 0], (0,5,4): [0, -1, 0],
            # top face (y = 1)
            (2,3,7): [0, 1, 0], (2,7,6): [0, 1, 0],
            # left face (x = -1)
            (0,7,3): [-1, 0, 0], (0,4,7): [-1, 0, 0],
            # right face (x = 1)
            (1,2,6): [1, 0, 0], (1,6,5): [1, 0, 0],
        }
        
        # Compute vertex normals by averaging face normals
        vertex_normals = np.zeros((8, 3), dtype=np.float32)
        vertex_face_count = np.zeros(8, dtype=np.int32)
        
        for (v0, v1, v2), normal in face_normals.items():
            for v in [v0, v1, v2]:
                vertex_normals[v] += normal
                vertex_face_count[v] += 1
        
        # Normalize
        for i in range(8):
            if vertex_face_count[i] > 0:
                vertex_normals[i] /= vertex_face_count[i]
                norm = np.linalg.norm(vertex_normals[i])
                if norm > 0:
                    vertex_normals[i] /= norm
        
        self.normals = vertex_normals.astype(np.float32)

    def upload(self):
        super().upload()