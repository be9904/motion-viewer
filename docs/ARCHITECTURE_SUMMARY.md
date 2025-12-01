# Object-Component-Transform Architecture Summary

## System Overview

A complete **Entity-Component-Transform** system with **hierarchical scene graph** support.

```
┌─────────────────────────────────────────────────────────────┐
│                        Scene Graph                          │
│                                                             │
│   Object "Root"                                             │
│   ├─ Transform (local position, rotation, scale)            │
│   ├─ Components (mesh, material, etc.)                      │
│   └─ Children                                               │
│       ├─ Object "Child1"                                    │
│       │   ├─ Transform (relative to parent)                 │
│       │   ├─ Components                                     │
│       │   └─ Children [...]                                 │
│       └─ Object "Child2"                                    │
│           ├─ Transform (relative to parent)                 │
│           └─ Components                                     │
└─────────────────────────────────────────────────────────────┘
```

## Core Classes

### 1. Transform Component
**Location:** `core/__init__.py`

Stores and manages local transformations (position, rotation, scale).

**Features:**
- Position stored as numpy array `[x, y, z]`
- Rotation stored as quaternion `[x, y, z, w]`
- Scale stored as numpy array `[sx, sy, sz]`
- Dirty flag optimization (only recalculates matrix when changed)
- Helper methods for common operations

**Methods:**
```python
transform = Transform(position, rotation, scale)
transform.set_position([x, y, z])
transform.set_rotation_euler([pitch, yaw, roll])  # degrees
transform.set_scale([x, y, z])
transform.translate([dx, dy, dz])
transform.rotate_euler([dpitch, dyaw, droll])
local_matrix = transform.get_local_matrix()  # Returns 4x4 matrix
```

### 2. Object Container
**Location:** `core/__init__.py`

Scene graph node that can contain components, plugins, and child objects.

**Features:**
- Built-in Transform component
- Component dictionary (meshes, materials, etc.)
- Plugin dictionary (behaviors, scripts)
- Parent-child relationships
- Automatic world matrix calculation
- Recursive update and draw

**Structure:**
```python
Object
├─ name: str
├─ transform: Transform
├─ components: dict[str, Any]
├─ plugins: dict[str, Plugin]
├─ parent: Object | None
├─ children: list[Object]
├─ _world_matrix: np.ndarray (cached)
└─ _world_dirty: bool (dirty flag)
```

**Methods:**
```python
# Creation
obj = Object(name, position, rotation, scale)

# Components
obj.add_component("mesh", sphere_mesh)
mesh = obj.get_component("mesh")

# Hierarchy
obj.add_child(child_obj)
obj.set_parent(parent_obj)

# Transform shortcuts
obj.set_position([x, y, z])
obj.translate([dx, dy, dz])
obj.set_rotation_euler([pitch, yaw, roll])

# Matrix getters
local_mat = obj.get_local_matrix()   # Local space (relative to parent)
world_mat = obj.get_world_matrix()   # World space (absolute)
world_pos = obj.get_world_position() # World position vector

# Lifecycle
obj.update()            # Update self and children
obj.draw(shader_prog)   # Draw self and children
```

## Transform Hierarchy Calculation

### Local to World Space

```
World Matrix = Parent's World Matrix × Local Matrix
```

**Example:**
```
Sun (root)
 └─ position: (0, 0, 0)
 └─ rotation: 45° around Y
 └─ World Matrix: T(0,0,0) * R(0,45,0)

    Earth (child of Sun)
     └─ position: (5, 0, 0)  [local, relative to Sun]
     └─ rotation: 23° around Y
     └─ World Matrix: Sun's World * T(5,0,0) * R(0,23,0)
     └─ World Position: ~(3.5, 0, 3.5)  [actual position in world]

        Moon (child of Earth)
         └─ position: (2, 0, 0)  [local, relative to Earth]
         └─ World Matrix: Earth's World * T(2,0,0)
         └─ World Position: calculated from full chain
```

### Dirty Flag Optimization

When a transform changes:
1. Mark local Transform as dirty
2. Mark Object's world matrix as dirty
3. Recursively mark all children as dirty

On next `get_world_matrix()` call:
- If dirty, recalculate from parent chain
- Cache result and clear dirty flag
- Only recalculate when needed (not every frame)

## Integration with Existing Systems

### With Mesh System

```python
# OLD WAY (direct mesh with transform)
sphere = Sphere(position=(5, 0, 0), rotation=(0, 45, 0), scale=(1, 1, 1))
sphere.draw(program)

# NEW WAY (Object with mesh component)
obj = core.Object("MySphere", position=(5, 0, 0), rotation=(0, 45, 0))
mesh = Sphere()  # Mesh doesn't need transform anymore
obj.add_component("mesh", mesh)
obj.draw(program)  # Object passes its world matrix to shader
```

### With Plugin System

```python
class MyScene(core.Plugin):
    def init(self):
        # Create objects
        self.root = core.Object("Root")
        # ... setup hierarchy
    
    def update(self):
        # Animate
        self.root.rotate_euler((0, 1, 0))
        
        # Draw (automatically sets uniforms)
        shader = core.SharedData.import_data("standard_shader")
        self.root.draw(shader.program)
```

### With Shader System

The `Object.draw()` method automatically:
1. Gets world matrix for this object
2. Sets `model_matrix` uniform in shader
3. Calls `component.draw()` for each drawable component
4. Recursively draws all children

## Usage Patterns

### Pattern 1: Independent Objects (No Hierarchy)

```python
objects = []
for i in range(10):
    obj = core.Object(f"Obj{i}", position=(i, 0, 0))
    obj.add_component("mesh", Cube())
    objects.append(obj)

# Each object has identity parent (world = local)
for obj in objects:
    obj.draw(shader.program)
```

### Pattern 2: Hierarchical Objects (Parent-Child)

```python
# Robot arm
shoulder = core.Object("Shoulder", position=(0, 2, 0))
shoulder.add_component("mesh", Sphere())

elbow = core.Object("Elbow", position=(0, 1.5, 0))  # relative to shoulder
elbow.add_component("mesh", Sphere())
shoulder.add_child(elbow)

hand = core.Object("Hand", position=(0, 1.5, 0))  # relative to elbow
hand.add_component("mesh", Sphere())
elbow.add_child(hand)

# Rotate shoulder -> entire arm moves
shoulder.rotate_euler((45, 0, 0))
shoulder.draw(shader.program)  # Draws all 3 parts
```

### Pattern 3: Dynamic Reparenting

```python
# Object can change parents at runtime
obj = core.Object("Dynamic")
obj.set_parent(parent1)  # Now child of parent1
# ... later
obj.set_parent(parent2)  # Now child of parent2
obj.set_parent(None)     # Now root object (no parent)
```

## Example Projects Included

### 1. Solar System (`projects/solarSystem/`)
Demonstrates hierarchical transforms with orbiting planets:
- Sun rotates on axis
- Earth orbits Sun AND rotates on axis
- Moon orbits Earth AND rotates on axis
- Mars orbits Sun independently

### 2. Cube Grid (`projects/cubeGrid/`)
Demonstrates independent objects:
- 5×5 grid of cubes and spheres
- Each object animated independently
- Wave effect based on position

## How to Use

### 1. In main.py
```python
# Import project
import projects.solarSystem as SOLAR

# Add to plugin queue
plugin_queue.append(SOLAR.SolarSystem())
```

### 2. Run your project
The Object system is now ready to use in any plugin!

## Benefits

✅ **Clean separation** - Transform logic separate from mesh/rendering
✅ **Reusable components** - Same mesh can be used by multiple objects
✅ **Hierarchical animation** - Move parent, children follow automatically
✅ **Performance** - Dirty flag prevents unnecessary recalculation
✅ **Flexible** - Easy to add new component types
✅ **Intuitive** - Local/world space handled automatically

## Next Steps

### Recommended Enhancements:

1. **Material System**
   - Add Material component
   - Store shader uniforms per object

2. **Scene Manager**
   - Root object container
   - Batch rendering by shader
   - Frustum culling

3. **Component Types**
   - Light component
   - Camera component
   - Script component (behaviors)
   - Collider component

4. **Serialization**
   - Save/load scene hierarchy to JSON
   - Prefab system

5. **Editor**
   - GUI for object hierarchy
   - Transform gizmos
   - Component inspector

## File Structure

```
core/
├─ __init__.py          # Transform, Object classes
├─ mesh.py              # Mesh classes (Cube, Sphere)
└─ shader.py            # Shader class

projects/
├─ solarSystem/
│   └─ __init__.py      # Hierarchical example
└─ cubeGrid/
    └─ __init__.py      # Multiple objects example

OBJECT_SYSTEM_USAGE.md  # Detailed usage guide
ARCHITECTURE_SUMMARY.md # This file
```

## Performance Considerations

1. **Matrix Calculation**
   - Only happens when transform changes (dirty flag)
   - Cached until next change
   - Children only recalculate if parent changed

2. **Hierarchy Depth**
   - Each level adds one matrix multiplication
   - Keep hierarchies shallow when possible
   - Typical limit: 10-20 levels

3. **Component Lookups**
   - Dictionary access is O(1)
   - Store frequently accessed components as members

4. **Drawing**
   - Minimize shader switches
   - Group objects by material/shader
   - Consider instancing for many identical objects

## Example of BVH Class Usage

```python
import core
from plugins.bvh_loader import BVHLoader

# 1. Setup
bvh = BVH()
bvh.load_from_path("assets/walk.bvh")

# 2. Main Loop
while not glfw.window_should_close(window):
    # ... standard gl setup ...

    # Update Animation
    bvh.update()

    # Draw
    # You only need to draw the root! 
    # core.Object automatically handles children and matrix multiplication.
    if bvh.root_object:
        bvh.root_object.draw(shader_program)
        
    # ... swap buffers ...
```