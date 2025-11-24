from OpenGL.GL import *
import numpy as np
from ctypes import c_void_p

import core

class Curve:
    def __init__(self, start_pos=(0.0, 0.0, 0.0), end_pos=(1.0, 0.0, 0.0), degree=1, color=(1,1,1), samples=100):
        # basic curve properties
        self.start_pos = np.array(start_pos, dtype=np.float32)
        self.end_pos = np.array(end_pos, dtype=np.float32)
        self.color = color
        
        # degree of curve. minimum 1
        self.degree = degree
        if degree < 1:
            print("WARNING: degree must be minimum 1. Degree has been set to 1 by default.")
            self.degree = 1
            
        # control points set based on degree
        self.control_points = self.generate_control_points()
            
        # gl related variables
        self.vao = None
        self.vbo = None
        self.samples = samples
        self.vertex_count = 2
        
        # built-in shader properties
        self.shader_program = self.create_shader()
        glUseProgram(self.shader_program)
        self.color_loc = glGetUniformLocation(self.shader_program, "uColor")
        
    def generate_control_points(self):
        # no control points if degree is 1 (straight line)
        if self.degree <= 1:
            return []
        
        # generate control points from start point, end point and degree
        points = []
        for i in range(1, self.degree):
            t = i / self.degree
            point = (1 - t) * self.start_pos + t * self.end_pos
            points.append(point.astype(np.float32))
            
        return points
    
    def find_curve_point(self, t): # bezier curve point by default (De Casteljau's Algorithm)
        pts = [self.start_pos] + self.control_points + [self.end_pos] # build the entire curve with all points
        points = np.array(pts, dtype=np.float32) # create a copy to prevent mutation
        n = len(points)
        for r in range(1, n): # De Casteljau's Algorithm
            points[:n-r] = (1-t) * points[:n-r] + t * points[1:n-r+1]
        return points[0]

    def sample_curve(self):
        if self.degree == 1: # degree = 1, simple line
            return np.array([self.start_pos, self.end_pos], dtype=np.float32)
        
        vertices = [self.find_curve_point(i / self.samples) for i in range(self.samples + 1)] # get each segment of curve point
        return np.array(vertices, dtype=np.float32)
    
    def init_curve(self):                        
        vertices = self.sample_curve() # curve segmentation with `self.samples`
        self.vertex_count = len(vertices) # save the number of vertex segments
        
        # generate buffers
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        
        # bind buffres
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
            
        # use shader program
        glUseProgram(self.shader_program)
        
        # set color uniform
        glUniform3fv(self.color_loc, 1, self.color)
            
        # draw curve
        glDrawArrays(GL_LINE_STRIP, 0, self.vertex_count)
        
    def create_shader(self):
        vertex_src = """
        #version 330 core
        layout (location = 0) in vec3 position;
        void main() {
            gl_Position = vec4(position, 1.0);
        }
        """

        fragment_src = """
        #version 330 core
        out vec4 FragColor;
        uniform vec3 uColor;
        void main() {
            FragColor = vec4(uColor, 1.0);
        }
        """

        # compile shaders
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_src)
        glCompileShader(vertex_shader)
        # check compile status omitted for brevity

        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_src)
        glCompileShader(fragment_shader)
        # check compile status omitted for brevity

        # link program
        program = glCreateProgram()
        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        glLinkProgram(program)

        # cleanup shaders
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
        
        return program

        
class Line(Curve):
    def __init__(self, start_pos=(0,0,0), end_pos=(1,0,0), samples=1):
        super().__init__(start_pos=start_pos, end_pos=end_pos, degree=1, samples=samples)