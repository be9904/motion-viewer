from OpenGL.GL import *
import os

class Shader:
    def __init__(self, vertex_path, fragment_path):
        self.program = None
        self.vertex_src = self.load_shader_source(vertex_path)
        self.fragment_src = self.load_shader_source(fragment_path)
        self.compile_and_link()

    @staticmethod
    def load_shader_source(path):
        with open(path, 'r') as f:
            return f.read()

    def compile_shader(self, source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        # check compilation
        result = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not result:
            error = glGetShaderInfoLog(shader).decode()
            raise RuntimeError(f"Shader compilation failed:\n{error}")
        return shader

    def compile_and_link(self):
        vert = self.compile_shader(self.vertex_src, GL_VERTEX_SHADER)
        frag = self.compile_shader(self.fragment_src, GL_FRAGMENT_SHADER)

        self.program = glCreateProgram()
        glAttachShader(self.program, vert)
        glAttachShader(self.program, frag)
        glLinkProgram(self.program)

        # check linking
        result = glGetProgramiv(self.program, GL_LINK_STATUS)
        if not result:
            error = glGetProgramInfoLog(self.program).decode()
            raise RuntimeError(f"Program linking failed:\n{error}")

        # shaders can be deleted after linking
        glDeleteShader(vert)
        glDeleteShader(frag)

    def use(self):
        glUseProgram(self.program)

    def set_uniform_matrix4fv(self, name, mat):
        loc = glGetUniformLocation(self.program, name)
        if loc != -1:
            glUniformMatrix4fv(loc, 1, GL_TRUE, mat)

    def set_uniform_vec4(self, name, vec):
        loc = glGetUniformLocation(self.program, name)
        if loc != -1:
            glUniform4fv(loc, 1, vec)
