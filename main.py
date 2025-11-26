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
from core.curve import *
import plugins.camera as _camera
import projects.helloCube as HELLO

#####################################
# Global Declarations
#####################################

plugin_queue = [] # plugin queue to loop at runtime

wnd = _window.Window() # create window
cam = _camera.Camera() # create camera
curve = Curve(start_pos=(0.0,0.0,0.0),end_pos=(50.0,0.0,0.0),degree=1,color=(1,1,1),samples=1)

#####################################
# Assemble Plugins
#####################################

# add camera to the front of queue
plugin_queue.append(cam)

# add plugins

# add projects
plugin_queue.append(HELLO.HelloCube())

#####################################
# Main Loop
#####################################

def call_plugins(queue, method_name):
    for plugin in queue:
        getattr(plugin, method_name)()

def mv_init():
    # initialize glfw window
    wnd.init()

    # init gl states
    glLineWidth(1.0)
    glClearColor(*_window.BG_COLOR)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    # set callbacks
    glfw.set_window_size_callback(wnd.window, core.resize)
    glfw.set_key_callback(wnd.window, core.keyboard)
    glfw.set_mouse_button_callback(wnd.window, core.mouse)
    glfw.set_cursor_pos_callback(wnd.window, core.cursor)

    # declare shader
    shader = core.Shader("shaders/std/std.vert", "shaders/std/std.frag")

    # exports
    core.SharedData.export_data("standard_shader", shader) # move to a project class
    
    # init axes
    curve.init_curve()

def mv_terminate():
    wnd.release()

if __name__ == "__main__":   
    mv_init()

    # Plugin.assemble()
    call_plugins(plugin_queue, "assemble")

    # Plugin.init()
    call_plugins(plugin_queue, "init")

    # Plugin.update(), Plugin.post_update()
    while not glfw.window_should_close(wnd.window):
        wnd.update()
        curve.draw_curve()
        call_plugins(plugin_queue, "update")
        
        wnd.post_update()
        call_plugins(plugin_queue, "post_update")

    # Plugin.reset() in certain conditions
    # call_plugins(plugin_queue, "reset")

    # Plugin.release() on reload
    call_plugins(plugin_queue, "release")

    mv_terminate()