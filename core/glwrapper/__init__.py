from OpenGL.GL import *
import numpy as np
import inspect

import core

# an OpenGL wrapper class that is always at the end of the plugin queue.
class GLWrapper(core.Plugin):
    _uniforms = {} # dictionary of { PROGRAM : { ULOC_1 : (UNIFORM_NAME_1, UNIFORM_1), ULOC_2 : (UNIFORM_NAME_2, UNIFORM_2), ... } }
    
    #####################################
    # CLASS METHODS
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
    def set_uniform(cls, program, uniform, name="name"):
        uloc = glGetUniformLocation( program, name )
        if uloc < 0:
            print(f"Unable to locate uniform {name}")
            return
            
        # locate uniform
        glUseProgram(program)
        
        # init update uniform
        if cls.update_uniform(uloc, uniform):
            cls._save_uniform(program, uloc, name, uniform) # append to _uniforms
    
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
                    glUniformMatrix2fv(uloc, 1, GL_FALSE, arr)
                elif (rows, cols) == (3, 3):
                    glUniformMatrix3fv(uloc, 1, GL_FALSE, arr)
                elif (rows, cols) == (4, 4):
                    glUniformMatrix4fv(uloc, 1, GL_FALSE, arr)
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
    
    #####################################
    # USER CALLBACKS
    #####################################
    
    def __init__(self):
        self.uniforms = []
        # member variables
    
    # assemble all configurations and files
    def assemble(self):
        # imports

        # exports

        return

    # setup basic settings before update loop
    def init(self):
        return

    # executed every frame
    def update(self):
        # update uniforms every frame
        for program in GLWrapper._uniforms.keys():
            GLWrapper.update_uniforms(program)
        return

    # executed at end of frame, after all plugin updates have looped
    def post_update(self):
        return

    # reset any modified parameters or files
    def reset(self):
        return

    # release runtime data
    def release(self):
        return
    