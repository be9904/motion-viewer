from abc import ABC, abstractmethod
from OpenGL.GL import glViewport, glGetUniformLocation, glUniformMatrix4fv, GL_FALSE
import glfw
import numpy as np
import quaternion as qt

from .util import *

#####################################
# PLUGIN
#####################################

class Plugin(ABC):
    def __init__(self):
        PluginQueue.register_callbacks(self)

    # assemble all configurations and files
    @abstractmethod
    def assemble(self, import_data):
        pass

    # setup basic settings (window, gui, logs etc)
    @abstractmethod
    def init(self):
        pass

    # executed every frame
    @abstractmethod
    def update(self):
        pass
    
    # executed at end of frame, after all plugin updates have looped
    def post_update(self):
        pass

    # reset any modified parameters or files
    def reset(self):
        pass

    # release runtime data
    @abstractmethod
    def release(self):
        pass
    
class PluginQueue:
    _plugin_queue = []
    
    @classmethod
    def register_callbacks(cls, plugin):
        if not isinstance(plugin, Plugin):
            raise TypeError(f"Expected a Plugin instance")
        cls._plugin_queue.append(plugin)
        return
    
    @classmethod
    def call_plugins(cls, method_name):
        for plugin in cls._plugin_queue:
            getattr(plugin, method_name)()

class SharedData:
    _data = {}
    _shaders = {}

    @classmethod
    def export_data(cls, name, value):
        cls._data[name] = value

    @classmethod
    def import_data(cls, name):
        return cls._data.get(name, None)
    
    @classmethod
    def export_shader(cls, name, value):
        if not isinstance(value, Shader):
            raise TypeError(f"Expected a Shader instance for '{name}', got {type(value).__name__}")
        cls._shaders[name] = value

    @classmethod
    def import_shader(cls, name):
        return cls._shaders.get(name, None)
    
    @classmethod
    def import_shaders(cls):
        shaders = []
        for shader in cls._shaders.values():
            shaders.append(shader)
        return shaders
    
    @classmethod # for debugging
    def list_data(cls):
        print(cls._data)
        
    @classmethod # for debugging
    def list_shaders(cls):
        print(cls._shaders)

class Transform:
    """Transform component for position, rotation, scale"""
    def __init__(self, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0, 1.0), scale=(1.0, 1.0, 1.0)):
        # Local transform (relative to parent)
        self.position = np.array(position, dtype=np.float32)
        
        # store rotation as quaternion (x, y, z, w)
        if len(rotation) == 3:
            # convert euler angles (degrees) to quaternion
            self.rotation = qt.from_euler_angles(
                np.radians(rotation[0]),
                np.radians(rotation[1]),
                np.radians(rotation[2])
            )
        else:
            # if already a quaternion
            self.rotation = np.array(rotation, dtype=np.float32)
        
        # scale of transform
        self.scale = np.array(scale, dtype=np.float32)
        
        # cached local matrix
        self._local_matrix = None
        self._dirty = True
    
    # get local transformation matrix (T * R * S)
    def get_local_matrix(self):
        if self._dirty:
            self._local_matrix = get_model_matrix(self.position, self.rotation, self.scale)
            self._dirty = False
        return self._local_matrix
    
    # set local position
    def set_position(self, position):
        self.position = np.array(position, dtype=np.float32)
        self._dirty = True
    
    # set rotation from euler angles (degrees)
    def set_rotation_euler(self, euler_angles):
        self.rotation = qt.from_euler_angles(
            np.radians(euler_angles[0]),
            np.radians(euler_angles[1]),
            np.radians(euler_angles[2])
        )
        self._dirty = True
    
    # set rotation from quaternion
    def set_rotation_quat(self, quaternion):
        self.rotation = np.array(quaternion, dtype=np.float32)
        self._dirty = True
    
    # set local scale
    def set_scale(self, scale):
        self.scale = np.array(scale, dtype=np.float32)
        self._dirty = True
    
    # move by delta amount
    def translate(self, delta):
        self.position += np.array(delta, dtype=np.float32)
        self._dirty = True
    
    # rotate by delta euler angles (degrees)
    def rotate_euler(self, delta_angles):
        delta_quat = qt.from_euler_angles(
            np.radians(delta_angles[0]),
            np.radians(delta_angles[1]),
            np.radians(delta_angles[2])
        )
        self.rotation = self.rotation * delta_quat
        self._dirty = True

class Object:
    def __init__(self, name, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
        self.name = name
        self.components = {}  # non-plugin components (meshes, etc.)
        self.plugins = {}     # plugin components
        self.parent = None    # parent Object
        self.children = []    # child Objects
        
        # every Object has a Transform by default
        self.transform = Transform(position, rotation, scale)
        
        # cached world matrix
        self._world_matrix = None
        self._world_dirty = True

    # add a component (mesh, material, etc.) to this object
    def add_component(self, name, comp):
        if isinstance(comp, Plugin):
            raise TypeError("Use add_plugin(plugin_name) instead.")
        
        if isinstance(comp, Object):
            raise TypeError("An Object cannot be added as a component. Use add_child() instead.")
        
        if name in self.components:
            print(f"Component with name '{name}' already exists")
            return False
        
        self.components[name] = comp
        return True

    # add a plugin component to this object
    def add_plugin(self, name, plugin):
        if not isinstance(plugin, Plugin):
            raise TypeError("Plugin must inherit from Plugin")
        
        if isinstance(plugin, Object):
            raise TypeError("An Object cannot be added as a Plugin")
        
        if name in self.plugins:
            print(f"Plugin with name '{name}' already exists")
            return False
        
        self.plugins[name] = plugin
        return True
    
    # get a component by name
    def get_component(self, name):
        return self.components.get(name, None)
    
    # get a plugin by name
    def get_plugin(self, name):
        return self.plugins.get(name, None)

    # add a child object (builds hierarchy)
    def add_child(self, obj):
        if not isinstance(obj, Object):
            raise TypeError("Child must be an Object")
        
        # remove from old parent if exists
        if obj.parent is not None:
            obj.parent.remove_child(obj)
        
        # set new parent relationship
        obj.parent = self
        self.children.append(obj)
        obj._mark_world_dirty()
        
        return obj
    
    # remove a child object
    def remove_child(self, obj):
        if obj in self.children:
            self.children.remove(obj)
            obj.parent = None
            obj._mark_world_dirty()
    
    # set parent object (inverse of add_child)
    def set_parent(self, obj):
        if obj is None:
            if self.parent:
                self.parent.remove_child(self)
        else:
            if not isinstance(obj, Object):
                raise TypeError("Parent must be an Object")
            obj.add_child(self)
    
    # mark world matrix as dirty (needs recalculation)
    def _mark_world_dirty(self):
        self._world_dirty = True
        # Propagate to children
        for child in self.children:
            child._mark_world_dirty()
    
    # get local transformation matrix
    def get_local_matrix(self):
        return self.transform.get_local_matrix()
    
    # get world transformation matrix (includes parent transforms)
    def get_world_matrix(self):
        if self._world_dirty:
            local = self.get_local_matrix()
            
            if self.parent is not None: # world = parent's world * local
                parent_world = self.parent.get_world_matrix()
                self._world_matrix = parent_world @ local
            else: # no parent = world matrix is local matrix
                self._world_matrix = local
            
            self._world_dirty = False
        
        return self._world_matrix
    
    # get position in world space
    def get_world_position(self):
        world_mat = self.get_world_matrix()
        return world_mat[:3, 3]
    
    # set local position
    def set_position(self, position):
        self.transform.set_position(position)
        self._mark_world_dirty()
    
    # set local rotation from euler angles
    def set_rotation_euler(self, euler_angles):
        self.transform.set_rotation_euler(euler_angles)
        self._mark_world_dirty()
    
    # set local scale
    def set_scale(self, scale):
        self.transform.set_scale(scale)
        self._mark_world_dirty()
    
    # move by delta amount in local space
    def translate(self, delta):
        self.transform.translate(delta)
        self._mark_world_dirty()
    
    # rotate by delta euler angles
    def rotate_euler(self, delta_angles):
        self.transform.rotate_euler(delta_angles)
        self._mark_world_dirty()
    
    # update this object and all children (call every frame if needed)
    def update(self):
        # update components
        for comp in self.components.values():
            if hasattr(comp, 'update'):
                comp.update()
        
        # update plugins
        for plugin in self.plugins.values():
            if hasattr(plugin, 'update'):
                plugin.update()
        
        # update children recursively
        for child in self.children:
            child.update()
    
    def draw(self, shader_program=None):
        # draw this object and all children
        # draw components with draw method (meshes etc.)
        for comp in self.components.values():
            if hasattr(comp, 'draw'):
                # pass world matrix to shader
                world_mat = self.get_world_matrix()
                if shader_program:
                    # set the model matrix uniform here
                    loc = glGetUniformLocation(shader_program, "model_matrix")
                    if loc != -1:
                        glUniformMatrix4fv(loc, 1, GL_FALSE, world_mat)
                    comp.draw(shader_program)
                else:
                    comp.draw()
        
        # draw children recursively
        for child in self.children:
            child.draw(shader_program)

#####################################
# USER CALLBACK FUNCTIONS
#####################################

def resize(window, width=1920, height=1080): # resize glfw window
    glViewport(0, 0, width, height)

def keyboard(window, key, scancode, action, mods): # keyboard callbacks
    if action == glfw.PRESS:
        print('key press')
    if action == glfw.RELEASE:
        print('key released')
    return

def mouse(window, button, action, mods): # mouse interactions
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            print("Enable LMB Functionality")
        if action == glfw.RELEASE:
            print("Disable LMB Functionality")

    if button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            print("Enable RMB Functionality")
        if action == glfw.RELEASE:
            print("Disable RMB Functionality")

    if button == glfw.MOUSE_BUTTON_MIDDLE:
        if action == glfw.PRESS:
            print("Enable MMB Functionality")
        if action == glfw.RELEASE:
            print("Disable MMB Functionality")
    return

def cursor(window, x, y): # cursor position
    return