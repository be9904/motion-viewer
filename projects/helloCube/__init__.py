import core
from core.mesh import *

class HelloCube(core.Plugin):
    def __init__(self):
        self.cube = Cube(position=(0,0,0),rotation=(0,0,0),scale=(1,1,1))
        self.camera = None
        self.shader = core.Shader("shaders/cel/cel.vert", "shaders/cel/cel.frag")
        
        # class member matrices
        self.model_matrix = None
        self.view_matrix = None
        self.projection_matrix = None
        
        # enable depth test and culling
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
    
    # assemble all configurations and files
    def assemble(self):
        self.camera = core.SharedData.import_data("camera")
        return

    # setup basic settings (window, gui, logs etc)
    def init(self):
        self.cube.upload()
        self.model_matrix = core.get_model_matrix(self.cube.position, self.cube.quaternion, self.cube.scale)
        
        if self.camera:
            self.view_matrix = core.get_view_matrix(self.camera)
            self.projection_matrix = core.get_projection_matrix(self.camera)
        return

    # executed every frame
    def update(self):
        if not self.camera or not self.cube:
            return

        # use shader program
        self.shader.use()
        
        # update matrices
        self.model_matrix = core.get_model_matrix(self.cube.position,
                                                self.cube.quaternion,
                                                self.cube.scale)
        self.view_matrix = core.get_view_matrix(self.camera)
        self.projection_matrix = core.get_projection_matrix(self.camera)

        # set uniforms using your helper
        self.shader.set_uniform_matrix4fv("model", self.model_matrix)
        self.shader.set_uniform_matrix4fv("view", self.view_matrix)
        self.shader.set_uniform_matrix4fv("projection", self.projection_matrix)
        
        # set lighting
        self.shader.set_uniform_vec4("lightPos", (5.0, 5.0, 5.0, 0.0))
        self.shader.set_uniform_vec4("lightColor", (1.0, 1.0, 1.0, 1.0))
        self.shader.set_uniform_vec4("objectColor", (1.0, 0.5, 0.31, 1.0))
        
        # bind cube VAO and draw
        glBindVertexArray(self.cube.vao)
        glDrawElements(GL_TRIANGLES, len(self.cube.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0) # unbind vao

    # reset any modified parameters or files
    def reset(self):
        return

    # release runtime data
    def release(self):
        return
