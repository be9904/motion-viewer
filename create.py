import os
import sys

INIT_TEMPLATE = \
'''import core
from .config import *

class {classname}(core.Plugin):
    def __init__(self):
        super().__init__() # remove after implementation
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
        return

    # reset any modified parameters or files
    def reset(self):
        return

    # release runtime data
    def release(self):
        return
'''
# CONFIG_TEMPLATE = \
# '''#####################################
# # CONFIGURATIONS
# #####################################
# '''

# converts a string to PascalCase.
def to_pascal_case(name):
    parts = name.replace("-", "_").split("_")
    return "".join(part.capitalize() for part in parts)

# creates plugin folder with __init__.py, config.py, main.py
def create_plugin(plugin_name, parent_dir="."):
    module_path = os.path.join(parent_dir, plugin_name)
    os.makedirs(module_path, exist_ok=True)

    # __init__.py
    classname = to_pascal_case(plugin_name)
    init_file = os.path.join(module_path, "__init__.py")
    with open(init_file, "w") as f:
        f.write(INIT_TEMPLATE.format(classname=classname))

    # # config.py
    # config_file = os.path.join(module_path, "config.py")
    # with open(config_file, "w") as f:
    #     f.write(CONFIG_TEMPLATE)

    print(f"Created Plugin: {plugin_name}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create.py {plugin_name}")
        sys.exit(1)

    plugin_name = sys.argv[1].strip()
    create_plugin(plugin_name, parent_dir="plugins")
