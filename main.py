#####################################
# List of Plugins
#####################################

import glfw
import plugins.window as _window
import plugins.camera as _camera

plugin_queue = []

wnd = _window.Window()
# plugin_queue.append({plugin})

cam = _camera.Camera(window=wnd)
plugin_queue.append(cam)

#####################################
# Assemble Plugins
#####################################

# setup renderer

# draw axes and grid plane

# setup camera

# setup trackball

# setup lighting

# add button for file selection

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

    # Plugin.update()
    while not glfw.window_should_close(wnd.window):
        wnd.update()
        call_plugins(plugin_queue, "update")

    # Plugin.reset() in certain conditions
    call_plugins(plugin_queue, "reset")

    # Plugin.release() on reload
    call_plugins(plugin_queue, "release")
    
    wnd.release()