# Object-Component-Transform System Usage Guide

## Overview
The Object system provides:
- **Hierarchical transforms** (parent-child relationships)
- **Local and world space transformations**
- **Component-based architecture** (add meshes, materials, etc.)
- **Automatic matrix calculation** with dirty flagging

## Basic Usage

### 1. Create Simple Object with Mesh

```python
import core
from core.mesh import Sphere, Cube

class MyScene(core.Plugin):
    def init(self):
        # Create an object with a sphere mesh
        sphere_obj = core.Object(
            name="MySphere",
            position=(0, 1, 0),
            rotation=(0, 0, 0),  # euler angles in degrees
            scale=(1, 1, 1)
        )
        
        # Add a mesh component
        sphere_mesh = Sphere(position=(0,0,0), scale=(1,1,1))
        sphere_obj.add_component("mesh", sphere_mesh)
        
        self.objects = [sphere_obj]
    
    def update(self):
        shader = core.SharedData.import_data("standard_shader")
        
        for obj in self.objects:
            obj.draw(shader.program)  # Automatically uses world matrix
```

### 2. Create Object Hierarchy (Parent-Child)

```python
def init(self):
    # Create parent object (solar system)
    sun = core.Object(
        name="Sun",
        position=(0, 0, 0),
        scale=(2, 2, 2)
    )
    sun_mesh = Sphere()
    sun.add_component("mesh", sun_mesh)
    
    # Create child object (planet)
    earth = core.Object(
        name="Earth",
        position=(5, 0, 0),  # 5 units away from parent
        scale=(0.5, 0.5, 0.5)
    )
    earth_mesh = Sphere()
    earth.add_component("mesh", earth_mesh)
    
    # Build hierarchy
    sun.add_child(earth)  # Earth is now a child of Sun
    
    # Create moon (child of Earth)
    moon = core.Object(
        name="Moon",
        position=(2, 0, 0),  # 2 units away from Earth
        scale=(0.2, 0.2, 0.2)
    )
    moon_mesh = Sphere()
    moon.add_component("mesh", moon_mesh)
    earth.add_child(moon)
    
    # Now we have: Sun -> Earth -> Moon
    self.sun = sun

def update(self):
    shader = core.SharedData.import_data("standard_shader")
    
    # Rotate sun (children rotate with it!)
    self.sun.rotate_euler((0, 1, 0))  # Rotate 1 degree per frame
    
    # Rotate earth around its own axis
    earth = self.sun.children[0]
    earth.rotate_euler((0, 2, 0))
    
    # Draw entire hierarchy with one call
    self.sun.draw(shader.program)  # Draws sun, earth, and moon
```

### 3. Local vs World Space

```python
def demonstrate_transforms(self):
    # Create parent at (10, 0, 0)
    parent = core.Object("Parent", position=(10, 0, 0))
    
    # Create child at local position (5, 0, 0)
    child = core.Object("Child", position=(5, 0, 0))
    parent.add_child(child)
    
    # Local space
    print(child.transform.position)  # [5, 0, 0] (relative to parent)
    
    # World space
    print(child.get_world_position())  # [15, 0, 0] (10 + 5)
```

### 4. Building a Complex Scene

```python
class RobotArm(core.Plugin):
    def init(self):
        # Base (root)
        self.base = core.Object("Base", position=(0, 0, 0))
        base_mesh = Cube(scale=(1, 0.5, 1))
        self.base.add_component("mesh", base_mesh)
        
        # Lower arm (child of base)
        self.lower_arm = core.Object("LowerArm", 
            position=(0, 1, 0),  # On top of base
            scale=(0.3, 2, 0.3)
        )
        lower_mesh = Cube()
        self.lower_arm.add_component("mesh", lower_mesh)
        self.base.add_child(self.lower_arm)
        
        # Upper arm (child of lower arm)
        self.upper_arm = core.Object("UpperArm",
            position=(0, 2, 0),  # On top of lower arm
            scale=(0.2, 1.5, 0.2)
        )
        upper_mesh = Cube()
        self.upper_arm.add_component("mesh", upper_mesh)
        self.lower_arm.add_child(self.upper_arm)
        
        # Hand (child of upper arm)
        self.hand = core.Object("Hand",
            position=(0, 1.5, 0),
            scale=(0.3, 0.3, 0.3)
        )
        hand_mesh = Sphere()
        self.hand.add_component("mesh", hand_mesh)
        self.upper_arm.add_child(self.hand)
        
        self.angle = 0
    
    def update(self):
        # Animate robot arm
        import math
        self.angle += 0.01
        
        # Rotate base (entire arm rotates)
        self.base.set_rotation_euler((0, math.sin(self.angle) * 45, 0))
        
        # Bend lower arm
        self.lower_arm.set_rotation_euler((math.sin(self.angle) * 30, 0, 0))
        
        # Bend upper arm
        self.upper_arm.set_rotation_euler((math.cos(self.angle) * 45, 0, 0))
        
        # Draw entire robot
        shader = core.SharedData.import_data("standard_shader")
        glUseProgram(shader.program)
        
        # Set camera matrices
        camera = core.SharedData.import_data("camera")
        shader.set_uniform_matrix4fv("view_matrix", camera.view)
        shader.set_uniform_matrix4fv("projection_matrix", camera.projection)
        
        # Draw hierarchy (automatically handles transforms)
        self.base.draw(shader.program)
```

### 5. Multiple Independent Objects

```python
class MultipleObjects(core.Plugin):
    def init(self):
        self.objects = []
        
        # Create grid of cubes
        for x in range(-3, 4):
            for z in range(-3, 4):
                obj = core.Object(
                    name=f"Cube_{x}_{z}",
                    position=(x * 2, 0, z * 2),
                    scale=(0.5, 0.5, 0.5)
                )
                mesh = Cube()
                obj.add_component("mesh", mesh)
                self.objects.append(obj)
    
    def update(self):
        shader = core.SharedData.import_data("standard_shader")
        camera = core.SharedData.import_data("camera")
        
        glUseProgram(shader.program)
        shader.set_uniform_matrix4fv("view_matrix", camera.view)
        shader.set_uniform_matrix4fv("projection_matrix", camera.projection)
        
        # Draw all objects
        for obj in self.objects:
            obj.draw(shader.program)
```

## API Reference

### Transform Class

```python
transform = core.Transform(position, rotation, scale)

# Setters (mark dirty automatically)
transform.set_position([x, y, z])
transform.set_rotation_euler([pitch, yaw, roll])  # degrees
transform.set_rotation_quat([x, y, z, w])
transform.set_scale([x, y, z])

# Incremental changes
transform.translate([dx, dy, dz])
transform.rotate_euler([dpitch, dyaw, droll])

# Get matrix
local_matrix = transform.get_local_matrix()  # 4x4 numpy array
```

### Object Class

```python
obj = core.Object(name, position, rotation, scale)

# Components
obj.add_component("mesh", sphere_mesh)
obj.add_component("material", material)
mesh = obj.get_component("mesh")

# Hierarchy
obj.add_child(child_obj)
obj.remove_child(child_obj)
obj.set_parent(parent_obj)

# Transforms (shortcuts to transform component)
obj.set_position([x, y, z])
obj.set_rotation_euler([pitch, yaw, roll])
obj.set_scale([sx, sy, sz])
obj.translate([dx, dy, dz])
obj.rotate_euler([dpitch, dyaw, droll])

# Get matrices
local_mat = obj.get_local_matrix()    # Local space
world_mat = obj.get_world_matrix()    # World space (includes parents)
world_pos = obj.get_world_position()  # World position as vector

# Lifecycle
obj.update()  # Update self and all children
obj.draw(shader_program)  # Draw self and all children
```

## Performance Tips

1. **Minimize hierarchy depth** - Each level adds matrix multiplication
2. **Group static objects** - Don't use hierarchy if objects don't move together
3. **Dirty flag optimization** - Matrices only recalculate when transforms change
4. **Batch by shader** - Group objects using same shader together

## Common Patterns

### Pattern 1: Static Scene
```python
# For objects that don't move, calculate once
obj = core.Object("Static", position=(5, 0, 0))
obj.add_component("mesh", mesh)
world_matrix = obj.get_world_matrix()  # Cached until transform changes
```

### Pattern 2: Animated Character
```python
# Root bone
root = core.Object("Root")
# Spine bones
spine1 = core.Object("Spine1", position=(0, 1, 0))
spine2 = core.Object("Spine2", position=(0, 1, 0))
root.add_child(spine1)
spine1.add_child(spine2)
# Animate by rotating bones
```

### Pattern 3: Vehicle with Wheels
```python
car = core.Object("Car", position=(0, 0, 0))
for i, pos in enumerate([(-1, 0, 1), (1, 0, 1), (-1, 0, -1), (1, 0, -1)]):
    wheel = core.Object(f"Wheel{i}", position=pos)
    wheel.add_component("mesh", cylinder_mesh)
    car.add_child(wheel)
# Move car -> wheels move with it
# Rotate individual wheels for animation
```

