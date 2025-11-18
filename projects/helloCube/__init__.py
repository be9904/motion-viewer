import core
from core.mesh import *

class HelloCube(core.Plugin):
    def __init__(self):
        self.cube = Cube(position=(0,0,0),rotation=(0,0,0),scale=(1,1,1))
        self.camera = None
        # enable depth and lighting once
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)

        glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 5, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # assemble all configurations and files
    def assemble(self):
        self.camera = core.SharedData.import_data("camera")
        return

    # setup basic settings (window, gui, logs etc)
    def init(self):
        self.MVP = core.get_mvp_matrix(self.cube.position, self.cube.quaternion, self.cube.scale, self.camera)
        return

    # executed every frame
    def update(self):
        if not self.camera or not self.cube:
            return

        glEnable(GL_DEPTH_TEST)
        
        # use shader program
        glUseProgram(self.shader_program)

        # get uniform locations
        model_loc = glGetUniformLocation(self.shader_program, "model")
        view_loc = glGetUniformLocation(self.shader_program, "view")
        proj_loc = glGetUniformLocation(self.shader_program, "projection")

        # model matrix
        model = core.get_model_matrix(self.cube)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model.T)

        # view & projection from camera
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, self.camera.view_matrix.T)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, self.camera.projection_matrix.T)

        # bind cube VAO and draw
        glBindVertexArray(self.cube.vao)
        glDrawElements(GL_TRIANGLES, len(self.cube.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        return

    # reset any modified parameters or files
    def reset(self):
        return

    # release runtime data
    def release(self):
        return
