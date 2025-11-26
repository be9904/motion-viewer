import core
from plugins.scene import Scene

class Player(core.Plugin):
    def __init__(self):
        # plugins
        self.scene = Scene()
    
    # assemble all configurations and files
    def assemble(self):
        self.scene.assemble()
        # imports

        # exports

        return

    # setup basic settings before update loop
    def init(self):
        return

    # executed every frame
    def update(self):
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
