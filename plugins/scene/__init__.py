import core

class Scene(core.Plugin):
    def __init__(self):
        # member variables
        self.objects = []
        self.axes = None # grid axes
        self.plane = None # grid plane

        # reference of shared data
        self.window = None
        self.camera = None
        self.std_shader = None
    
    # assemble all configurations and files
    def assemble(self):
        # imports
        self.window = core.SharedData.import_data("window")
        self.camera = core.SharedData.import_data("camera")
        self.std_shader = core.SharedData.import_shader("std_shader")

        # exports
        core.SharedData.export_data("scene_objects", self.objects)
        return

    # setup basic settings before update loop
    def init(self):
        # locate all uniforms
        return

    # executed every frame
    def update(self):
        return

    # reset any modified parameters or files
    def reset(self):
        return

    # release runtime data
    def release(self):
        return
