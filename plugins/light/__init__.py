from OpenGL.GL import *

import core

class Light(core.Plugin):
    def __init__(self, position=(1.0, -1.0, 1.0, 0.0)):
        self.position = position
        self.color = (1,1,1)
        self.intensity = 1.0

        # Uniform caching
        self.gl_position = None
        self.gl_color = None
        self.gl_intensity = None
    
    # assemble all configurations and files
    def assemble(self):
        # imports
        self.shader = core.SharedData.import_data("std_shader")
        
        # exports

        return

    # setup basic settings before update loop
    def init(self):
        glUseProgram(self.shader.program)
        self.gl_position = glGetUniformLocation(self.shader.program, "light_position")
        self.gl_color = glGetUniformLocation(self.shader.program, "light_color")
        self.gl_intensity = glGetUniformLocation(self.shader.program, "light_intensity")

        if self.gl_position == -1:
            print(f"{self.__class__.__name__}: Failed to locate light_position from shader")
        else:
            glUniform4fv(self.gl_position, 1, self.position)

        if self.gl_color == -1:
            print(f"{self.__class__.__name__}: Failed to locate light_color from shader")
        else:
            glUniform3fv(self.gl_color, 1, self.color)

        if self.gl_intensity == -1:
            print(f"{self.__class__.__name__}: Failed to locate light_intensity from shader")
        else:
            glUniform1f(self.gl_intensity, 1, self.intensity)

        return

    # executed every frame
    def update(self):
        glUseProgram(self.shader.program)
        if self.gl_position != -1:
            glUniform4fv(self.gl_position, 1, self.position)
        return

    # reset any modified parameters or files
    def reset(self):
        self.position = (1.0, -1.0, 1.0, 0.0)
        return

    # release runtime data
    def release(self):
        self.position = None
        
        self.gl_position = None
        return
