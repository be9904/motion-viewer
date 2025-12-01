# Object System - Quick Start Guide

## 3-Step Usage

### Step 1: Create Object with Transform
```python
obj = core.Object(
    name="MyObject",
    position=(x, y, z),
    rotation=(pitch, yaw, roll),  # degrees
    scale=(sx, sy, sz)
)
```

### Step 2: Add Components (Mesh, etc.)
```python
mesh = Sphere()  # or Cube()
obj.add_component("mesh", mesh)
```

### Step 3: Draw It
```python
obj.draw(shader.program)  # Automatically uses world transform
```

## Complete Example

```python
import core
from core.mesh import Sphere, Cube

class MyProject(core.Plugin):
    def assemble(self):
        self.camera = core.SharedData.import_data("camera")
        self.shader = core.SharedData.import_data("standard_shader")
    
    def init(self):
        # Create object with sphere mesh
        self.obj = core.Object("MySphere", position=(0, 1, 0))
        mesh = Sphere()
        self.obj.add_component("mesh", mesh)
    
    def update(self):
        # Animate
        self.obj.rotate_euler((0, 1, 0))  # Spin 1° per frame
        
        # Render
        glUseProgram(self.shader.program)
        self.shader.set_uniform_matrix4fv("view_matrix", self.camera.view)
        self.shader.set_uniform_matrix4fv("projection_matrix", self.camera.projection)
        
        self.obj.draw(self.shader.program)
```

## Hierarchy Example

```python
# Parent
parent = core.Object("Parent", position=(0, 0, 0))
parent.add_component("mesh", Cube())

# Child (relative to parent)
child = core.Object("Child", position=(3, 0, 0))
child.add_component("mesh", Sphere())
parent.add_child(child)

# Move parent -> child moves too!
parent.translate((1, 0, 0))

# Draw both with one call
parent.draw(shader.program)
```

## Common Operations

```python
# Position
obj.set_position([x, y, z])
obj.translate([dx, dy, dz])
pos = obj.get_world_position()

# Rotation
obj.set_rotation_euler([pitch, yaw, roll])  # degrees
obj.rotate_euler([dpitch, dyaw, droll])

# Scale
obj.set_scale([sx, sy, sz])

# Hierarchy
parent.add_child(child)
child.set_parent(parent)

# Components
obj.add_component("mesh", mesh)
mesh = obj.get_component("mesh")
```

## Test Projects

Run these to see it in action:

### Solar System (Hierarchy Demo)
```python
# In main.py
import projects.solarSystem as SOLAR
plugin_queue.append(SOLAR.SolarSystem())
```

### Cube Grid (Multiple Objects Demo)
```python
# In main.py
import projects.cubeGrid as GRID
plugin_queue.append(GRID.CubeGrid())
```

## Key Concepts

1. **Local Space** = Transform relative to parent
2. **World Space** = Absolute position in scene
3. **Hierarchy** = Parent transform affects children
4. **Components** = Things attached to objects (mesh, material, etc.)

## That's It!

- ✅ Hierarchical transforms
- ✅ Component-based architecture  
- ✅ Automatic matrix calculation
- ✅ Clean separation of concerns

Read `OBJECT_SYSTEM_USAGE.md` for detailed examples and `ARCHITECTURE_SUMMARY.md` for the complete system design.