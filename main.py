#####################################
# List of Plugins
#####################################

import glfw
import plugins.window as _window

plugin_queue = []

wnd = _window.Window()
# plugin_queue.append({plugin})

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

if __name__ == "__main__":
    # Plugin.init()
    wnd.init()

    # Plugin.assemble()
    for plugin in plugin_queue:
        plugin.assemble()

    # Plugin.update()
    while not glfw.window_should_close(wnd.window):
        wnd.update()
        for plugin in plugin_queue:
            plugin.update()

    # Plugin.reset() in certain conditions

    # Plugin.release() on reload
    for plugin in plugin_queue:
        plugin.release()
    wnd.release()