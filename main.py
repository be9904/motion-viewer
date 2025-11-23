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
import plugins.camera as _camera
import projects.helloCube as HELLO

#####################################
# Assemble Plugins
#####################################

# plugin queue to loop at runtime
plugin_queue = []

# shared data that is passed between plugins
shared_data = core.SharedData()

# setup window
wnd = _window.Window()

# setup camera
cam = _camera.Camera(window=wnd)
plugin_queue.append(cam)

# add projects
plugin_queue.append(HELLO.HelloCube())

# declare shader
shader = core.Shader("shaders/cel/cel.vert", "shaders/cel/cel.frag")

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

    # export shader data
    core.SharedData.export_data("shader", shader)

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
        call_plugins(plugin_queue, "update")
        
        wnd.post_update()
        call_plugins(plugin_queue, "post_update")

    # Plugin.reset() in certain conditions
    # call_plugins(plugin_queue, "reset")

    # Plugin.release() on reload
    call_plugins(plugin_queue, "release")

    mv_terminate()