import core
import numpy as np
import quaternion as qt
from core.mesh import Sphere
from core.curve import Line

class Joint(core.Object):
    def __init__(self, name, position=(0.0, 0.0, 0.0)):
        # 1. Initialize the base Object (sets up Transform, Parent/Child lists, etc.)
        super().__init__(name, position=position)
        
        # 2. BVH Specific Data
        # Store the initial offset (rest position) separately from the active transform
        self.rest_offset = np.array(position, dtype=np.float32)
        
        # Channel parsing data
        self.channels = []       # e.g., ['Xposition', 'Zrotation', ...]
        self.channel_order = ""  # e.g., "ZXY"
        
        # 3. Default Visualization
        # Automatically add a Sphere component so we can see the joint
        self.add_component("joint_viz", Sphere(scale=(0.2, 0.2, 0.2)))

    def create_bone_connection(self, child_offset):
        """
        Creates a visual line connecting this joint to its child.
        """
        # Create a line from local (0,0,0) to the child's local offset
        # We assume child_offset is the relative position of the child
        bone_visual = Line(
            start_pos=(0, 0, 0), 
            end_pos=child_offset, 
            color=(0.7, 0.7, 0.7)
        )
        
        # Initialize the curve buffers (required by your curve.py)
        bone_visual.init_curve()
        
        # Add as a component. unique name based on offset to avoid conflicts
        comp_name = f"bone_to_{child_offset[0]:.2f}_{child_offset[1]:.2f}"
        self.add_component(comp_name, bone_visual)

    def set_pose_from_frame(self, frame_data, data_ptr):
        """
        Updates the Joint's transform based on a slice of frame data.
        Returns the updated data_ptr.
        """
        # Start with rest position
        pos = self.rest_offset.copy()
        
        # Accumulate rotations
        # We use a dictionary to capture values irrespective of order
        rot_vals = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
        
        for channel in self.channels:
            val = frame_data[data_ptr]
            data_ptr += 1
            
            if channel == "Xposition": pos[0] = val
            elif channel == "Yposition": pos[1] = val
            elif channel == "Zposition": pos[2] = val
            elif channel == "Xrotation": rot_vals['X'] = val
            elif channel == "Yrotation": rot_vals['Y'] = val
            elif channel == "Zrotation": rot_vals['Z'] = val

        # Apply Position (Mix of Rest Offset + Motion Data)
        self.set_position(pos)
        
        # Apply Rotation (Respecting BVH Euler Order)
        # Start with Identity
        final_quat = np.quaternion(1, 0, 0, 0)
        
        # If no specific order found, default to ZXY (common in BVH)
        order = self.channel_order if self.channel_order else "ZXY"

        for axis in order:
            angle_rad = np.radians(rot_vals[axis])
            if axis == 'X':
                q = qt.from_euler_angles(angle_rad, 0, 0)
            elif axis == 'Y':
                q = qt.from_euler_angles(0, angle_rad, 0)
            elif axis == 'Z':
                q = qt.from_euler_angles(0, 0, angle_rad)
            final_quat = final_quat * q
            
        # Update Core Transform
        self.transform.set_rotation_quat(qt.as_float_array(final_quat))
        
        return data_ptr
