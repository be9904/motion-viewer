#####################################
# Plugins & Libraries
#####################################

# library imports
import glfw

# local imports
import core.window as _window
import plugins.camera as _camera
import projects.helloCube as HELLO
import projects.helloCube2 as HELLO2

#####################################
# Assemble Plugins
#####################################

# plugin queue to loop at runtime
plugin_queue = []

# setup window
wnd = _window.Window()

# setup camera
cam = _camera.Camera(window=wnd)
plugin_queue.append(cam)

# add button for file selection

# add projects
plugin_queue.append(HELLO.HelloCube())
plugin_queue.append(HELLO2.HelloCube2())

#####################################
# Main Loop
#####################################

def call_plugins(plugin_queue, method_name):
    for plugin in plugin_queue:
        getattr(plugin, method_name)()

if __name__ == "__main__":    
    wnd.init()

    # Plugin.init()
    call_plugins(plugin_queue, "init")

    # Plugin.assemble()
    call_plugins(plugin_queue, "assemble")

    # Plugin.update(), .post_update()
    while not glfw.window_should_close(wnd.window):
        wnd.update()
        call_plugins(plugin_queue, "update")
        
        wnd.post_update()
        call_plugins(plugin_queue, "post_update")

    # Plugin.reset() in certain conditions
    call_plugins(plugin_queue, "reset")

    # Plugin.release() on reload
    call_plugins(plugin_queue, "release")
    
    wnd.release()