#####################################
# Plugins & Libraries
#####################################

# library imports
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

# local imports
import core
import core.window as _window
from core.glwrapper import GLWrapper as glw
from core.curve import *
import plugins.camera as _camera

# project imports
# from projects.bvhviewer import BVHViewer
from projects.test import Test

#####################################
# Global Declarations
#####################################

shaders = []

mv_window = _window.Window() # create window
viewport_cam = _camera.Camera() # create camera

#####################################
# Assemble Plugins & Projects
#####################################

# add plugins

# add projects
test = Test()

#####################################
# Main Loop
#####################################

def mv_init():
    # initialize glfw window
    mv_window.init()

    # init gl states
    glw.init()

    # set callbacks
    glfw.set_window_size_callback(mv_window.glfw_window, core.resize)
    glfw.set_key_callback(mv_window.glfw_window, core.keyboard)
    glfw.set_mouse_button_callback(mv_window.glfw_window, core.mouse)
    glfw.set_cursor_pos_callback(mv_window.glfw_window, core.cursor)

    # declare shaders and export
    shader = core.Shader("shaders/std/std.vert", "shaders/std/std.frag")
    core.SharedData.export_shader("std_shader", shader) # set the default shader (fallback)

def mv_terminate():
    mv_window.release()

if __name__ == "__main__":   
    # init the motion viewer
    mv_init()
    
    # reference shaders
    shaders += core.SharedData.import_shaders()

    # Plugin.assemble()
    print(core.PluginQueue._plugin_queue)
    core.PluginQueue.call_plugins("assemble")

    # Plugin.init()
    core.PluginQueue.call_plugins("init")
    
    # setup camera matrices
    for shader in shaders:
        glw.set_uniform(shader.program, viewport_cam.view, "view_matrix")
        glw.set_uniform(shader.program, viewport_cam.projection, "projection_matrix")

    # Plugin.update(), Plugin.post_update()
    while not glfw.window_should_close(mv_window.glfw_window):
        mv_window.update()
        core.PluginQueue.call_plugins("update")
        glw.update() # update uniforms

        mv_window.post_update()
        core.PluginQueue.call_plugins("post_update")

    # Plugin.reset() in certain conditions
    # call_plugins(plugin_queue, "reset")

    # Plugin.release() on reload
    core.PluginQueue.call_plugins("release")

    mv_terminate()