from OpenGL.GL import *
import numpy as np
from ctypes import c_void_p

class Curve:
    def __init__(self, start_pos=(0.0, 0.0, 0.0), end_pos=(1.0, 0.0, 0.0), degree=1, samples=100):
        self.start_pos = np.array(start_pos, dtype=np.float32)
        self.end_pos = np.array(end_pos, dtype=np.float32)
        self.degree = degree
        if degree < 1:
            print("WARNING: degree must be minimum 1. Degree has been set to 1 by default.")
            self.degree = 1
        self.control_points = self.generate_control_points()
            
        # gl related variables
        self.vao = None
        self.vbo = None
        self.samples = samples
        self.vertex_count = 2
        
    def generate_control_points(self):
        if self.degree <= 1:
            return []
        
        points = []
        for i in range(1, self.degree):
            t = i / self.degree
            point = (1 - t) * self.start_pos + t * self.end_pos
            points.append(point.astype(np.float32))
            
        return points
    
    def find_curve_point(self, t, points): # bezier curve point by default (De Casteljau's Algorithm)
        pts = [self.start_pos] + self.control_points + [self.end_pos]
        points = np.array(pts, dtype=np.float32)
        n = len(points)
        for r in range(1,n):
            points[:n-r] = (1 - t) * points[:n-r] + t * points[1:n-r+1]
        return points[0]
    
    def sample_curve(self):
        if self.degree == 1: # degree = 1, simple line
            return np.array([self.start_pos, self.end_pos], dtype=np.float32)
        
        # generate full set of points
        points = [self.start_pos] + self.control_points + [self.end_pos]
        
        vertices = []
        for i in range(self.samples + 1):
            t = i / self.samples
            vertices.append(self.find_curve_point(t))
        return np.array(vertices, dtype=np.float32)
    
    def init_curve(self):
        vertices = self.sample_curve()
        self.vertex_count = len(vertices)
        
        # generate buffers
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 12, c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw_curve(self):
        if self.vao is not None:
            glBindVertexArray(self.vao)
            
        glDrawArrays(GL_LINE_STRIP, 0, self.vertex_count)
        
class Line(Curve):
    def __init__(self, start_pos=(0,0,0), end_pos=(1,0,0), samples=1):
        super().__init__(start_pos=start_pos, end_pos=end_pos, degree=1, samples=samples)