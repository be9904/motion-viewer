from OpenGL.GL import *
import numpy as np
import inspect

# an OpenGL wrapper class that is always at the end of the plugin queue.
class GLWrapper:
    _uniforms = {} # dictionary of { PROGRAM : { ULOC_1 : (UNIFORM_NAME_1, UNIFORM_1), ULOC_2 : (UNIFORM_NAME_2, UNIFORM_2), ... } }
    _instance_uniforms = {} # { PROGRAM : [ (ULOC_1, VAO_1, UNIFORM_1, IDX_COUNT_1), (ULOC_2, VAO_2, UNIFORM_2, IDX_COUNT_2) ... ] }
    
    #####################################
    # WRAPPER FUNCTIONS
    #####################################
    
    @classmethod
    def _save_uniform(cls, program, uloc, name, uniform):
        # print a warning if called directly
        caller = inspect.stack()[1].function
        if caller != "set_uniform":
            print("WARNING: This function should not be called directly.")
            print("Use set_uniform() instead")
        
        # check if key does not exist
        if program not in cls._uniforms:
            cls._uniforms[program] = {}
        
        # add to dictionary
        cls._uniforms[program][uloc] = (name, uniform)
        
    @classmethod
    def _save_instance_uniform(cls, program, uloc, vao, uniform, idx_count):
        # print a warning if called directly
        caller = inspect.stack()[1].function
        if caller != "set_instance_uniform":
            print("WARNING: This function should not be called directly.")
            print("Use set_instance_uniform() instead")
            
        # check if key does not exist
        if program not in cls._instance_uniforms:
            cls._instance_uniforms[program] = []
            
        cls._instance_uniforms[program].append((uloc, vao, uniform, idx_count))

    @classmethod
    def set_uniform(cls, program, uniform, name="name"):
        uloc = glGetUniformLocation( program, name )
        if uloc < 0:
            print(f"{inspect.currentframe().f_code.co_name}: Unable to locate uniform {name}")
            return
            
        # locate uniform
        glUseProgram(program)
        
        # init update uniform
        if cls.update_uniform(uloc, uniform):
            cls._save_uniform(program, uloc, name, uniform) # append to _uniforms
            
    @classmethod
    def set_instance_uniform(cls, program, vao, uniform, idx_count, name="name"):
        uloc = glGetUniformLocation( program, name )
        if uloc < 0:
            print(f"{inspect.currentframe().f_code.co_name}: Unable to locate uniform {name}")
            
        # locate uniform
        glUseProgram(program)
        
        # init update instance uniform
        if cls.update_uniform(uloc, uniform):
            cls._save_instance_uniform(program, uloc, vao, uniform, idx_count) # append to _instance_uniforms
    
    @classmethod
    def update_uniform(cls, uloc, uniform):
        # scalars
        if isinstance(uniform, bool):
            glUniform1i(uloc, int(uniform))
            return True

        if isinstance(uniform, int):
            glUniform1i(uloc, uniform)
            return True

        if isinstance(uniform, float):
            glUniform1f(uloc, uniform)
            return True
        
        # sequences
        if isinstance(uniform, (tuple, list, np.ndarray)):
            arr = np.array(uniform)

            # VECTOR uniforms
            if arr.ndim == 1:  
                length = arr.shape[0]
                if length == 2:
                    glUniform2fv(uloc, 1, arr)
                elif length == 3:
                    glUniform3fv(uloc, 1, arr)
                elif length == 4:
                    glUniform4fv(uloc, 1, arr)
                else:
                    print(f"Unsupported vector size: {length}")
                    return False
                return True

            # MATRIX uniforms
            if arr.ndim == 2:
                rows, cols = arr.shape
                if (rows, cols) == (2, 2):
                    glUniformMatrix2fv(uloc, 1, GL_TRUE, arr)
                elif (rows, cols) == (3, 3):
                    glUniformMatrix3fv(uloc, 1, GL_TRUE, arr)
                elif (rows, cols) == (4, 4):
                    glUniformMatrix4fv(uloc, 1, GL_TRUE, arr)
                else:
                    print(f"Unsupported matrix size: {arr.shape}")
                    return False
                return True
            
        print(f"Unsupported uniform type for '{uloc}': {type(uniform)}")
        return False
    
    @classmethod
    def update_uniforms(cls, program): # per program uniform update
        # locate program in _uniforms
        uniforms = cls._uniforms.get(program)
        if uniforms is None:
            print(f"No uniforms found for program {program}")
            uniforms = {}
            
        # update all uniforms in 'program'
        glUseProgram(program)
        for uloc, uniform_pair in uniforms.items():
            cls.update_uniform(uloc, uniform_pair[1])
            
    @classmethod
    def draw_instances(cls, program):
        # notify which program (safety check)  
        glUseProgram(program)
        
        # loop over each instance registered for this program
        instance_dicts = cls._instance_uniforms.get(program)
        if instance_dicts is None:
            # nothing to draw
            glBindVertexArray(0)
            return
        
        # update per instance uniforms
        for i_uloc, i_vao, i_uniform, i_idx_count in cls._instance_uniforms[program]:
            glBindVertexArray(i_vao)
            cls.update_uniform(i_uloc, i_uniform)
        
            # draw elements using bound VAO and previously stored index count
            # assumes the VAO has its index buffer set up
            glDrawElements(GL_TRIANGLES, i_idx_count, GL_UNSIGNED_INT, None)
            
        # unbind VAO for safety
        glBindVertexArray(0)
        return
    
    #####################################
    # CALLBACKS
    #####################################
    
    # def __init__(self):
    #     # member variables
    #     self.shaders = []
    
    # # assemble all configurations and files
    # def assemble(self):
    #     # imports
    #     _shaders = core.SharedData.import_shader()
    #     for shader in _shaders.values():
    #         self.shaders.append(shader)

    #     # exports

    #     return

    @classmethod
    # setup basic settings before update loop
    def init(self):
        # init gl states
        glLineWidth(1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        return

    @classmethod
    # executed every frame
    def update(self):
        # update uniforms every frame
        for program in GLWrapper._uniforms.keys():
            GLWrapper.update_uniforms(program)
            GLWrapper.draw_instances(program)

    # # executed at end of frame, after all plugin updates have looped
    # def post_update(self):
    #     return

    # # reset any modified parameters or files
    # def reset(self):
    #     return

    # # release runtime data
    # def release(self):
    #     return
    