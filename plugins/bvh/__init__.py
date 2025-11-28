import time
import numpy as np
import quaternion as qt # Assuming numpy-quaternion is available as per your core imports

import core
from core.mesh import Sphere
from plugins.joint import Joint

class BVH(core.Plugin):
    def __init__(self):
        super().__init__()
        self.root_object = None 
        self.file_content = ""
        self.lines = []
        self._line_idx = 0
        
        # Animation Data
        self.frames = []
        self.frame_time = 0.033
        self.start_time = 0
        self.is_playing = False
        
        # Mapping for animation: List of dicts
        # [{'object': core.Object, 'channels': ['Xposition', 'Zrotation', ...], 'order': 'ZXY'}]
        self.animated_nodes = [] 

    def assemble(self, import_data):
        # In a real app, you might import a file path here
        pass

    def init(self):
        # Example initialization if file_content is set externally
        if self.file_content:
            self.load_from_string(self.file_content)

    def load_from_path(self, path):
        with open(path, 'r') as f:
            self.load_from_string(f.read())

    def load_from_string(self, content):
        self.lines = [l.strip() for l in content.split('\n') if l.strip()]
        self.frames = []
        self.animated_nodes = []
        self._line_idx = 0
        
        # 1. Parse Hierarchy
        if self.lines and self.lines[0] == "HIERARCHY":
            self._line_idx = 1
            self.root_object = self.parse_hierarchy(None)
        
        # 2. Parse Motion
        try:
            motion_idx = self.lines.index("MOTION")
            self._line_idx = motion_idx + 1
            self.parse_motion()
            self.is_playing = True
            self.start_time = time.time()
            print(f"BVH Loaded: {len(self.frames)} frames, {len(self.animated_nodes)} animated joints.")
        except ValueError:
            print("BVH Error: No MOTION section found.")

    def update(self):
        # if not self.is_playing or not self.frames or not self.root_object:
        #     return

        # # 1. Calculate Frame Index
        # elapsed = time.time() - self.start_time
        # frame_idx = int(elapsed / self.frame_time) % len(self.frames)
        # current_frame_data = self.frames[frame_idx]
        
        # data_ptr = 0

        # # 2. Apply Motion to Objects
        # for node in self.animated_nodes:
        #     obj = node['object']
        #     channels = node['channels']
            
        #     # Start with the Rest Pose Position (OFFSET)
        #     # We copy it so we don't mutate the original rest offset
        #     pos = np.array(obj.rest_offset, dtype=np.float32)
            
        #     # Dictionary to temporarily hold rotation values for this frame
        #     rot_vals = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
            
        #     for channel in channels:
        #         val = current_frame_data[data_ptr]
        #         data_ptr += 1
                
        #         if channel == "Xposition": pos[0] = val
        #         elif channel == "Yposition": pos[1] = val
        #         elif channel == "Zposition": pos[2] = val
        #         elif channel == "Xrotation": rot_vals['X'] = val
        #         elif channel == "Yrotation": rot_vals['Y'] = val
        #         elif channel == "Zrotation": rot_vals['Z'] = val

        #     # Apply Position
        #     # Note: BVH motion data for Root position is usually absolute, 
        #     # while children rely on their parent's transform + their offset.
        #     # If channels had position, we use the parsed 'pos'. 
        #     # If not, 'pos' remains the 'rest_offset'.
        #     obj.set_position(pos)

        #     # Apply Rotation
        #     # We must respect the channel order (e.g. Zrotation, then X, then Y)
        #     # The node['channel_order'] stores e.g. "ZXY"
            
        #     # Start with Identity Quaternion
        #     final_quat = np.quaternion(1, 0, 0, 0) 
            
        #     # Apply rotations in the specific order defined by BVH
        #     for axis in node['channel_order']:
        #         angle_rad = np.radians(rot_vals[axis])
                
        #         if axis == 'X':
        #             q = qt.from_euler_angles(angle_rad, 0, 0)
        #         elif axis == 'Y':
        #             q = qt.from_euler_angles(0, angle_rad, 0)
        #         elif axis == 'Z':
        #             q = qt.from_euler_angles(0, 0, angle_rad)
                
        #         # Multiply current rotation by new axis rotation
        #         final_quat = final_quat * q

        #     obj.transform.set_rotation_quat(qt.as_float_array(final_quat))
        return

    def release(self):
        self.root_object = None
        self.frames = []
        self.animated_nodes = []

    # -----------------------------------------------------------
    # Parsing Logic
    # -----------------------------------------------------------

    def parse_hierarchy(self, parent_obj):
        line = self.lines[self._line_idx]
        self._line_idx += 1
        
        parts = line.split()
        is_end_site = line.startswith("End Site")
        name = "EndSite" if is_end_site else (parts[1] if len(parts) > 1 else "Unknown")
        
        # --- CREATE CORE OBJECT ---
        obj = Joint(name)
        
        # Add visual component (Sphere)
        # Make joints smaller (0.2) so they look like nodes
        obj.add_component("mesh", Sphere(scale=(0.2, 0.2, 0.2)))

        if parent_obj:
            parent_obj.add_child(obj)
            
        if self.lines[self._line_idx] != "{": raise ValueError("Expected '{'")
        self._line_idx += 1

        channels = []
        channel_order = "XYZ" # Default
        
        while self._line_idx < len(self.lines):
            line = self.lines[self._line_idx]
            
            if line.startswith("OFFSET"):
                parts = line.split()
                # Parse Offset
                offset = [float(parts[1]), float(parts[2]), float(parts[3])]
                
                # Store as Rest Offset (custom property on the object)
                obj.rest_offset = offset
                
                # Set initial position
                obj.set_position(offset)
                self._line_idx += 1

            elif line.startswith("CHANNELS"):
                parts = line.split()
                channels = parts[2:] # Skip "CHANNELS" and count
                
                # Determine Rotation Order (e.g., extracts "Z" from "Zrotation")
                rot_channels = [ch[0] for ch in channels if "rotation" in ch]
                if rot_channels:
                    channel_order = "".join(rot_channels)
                
                self._line_idx += 1

            elif line.startswith("JOINT") or line.startswith("End Site"):
                self.parse_hierarchy(obj) # Recurse

            elif line == "}":
                self._line_idx += 1
                break
            else:
                self._line_idx += 1

        # Register for animation updates if this joint has channels
        if channels:
            self.animated_nodes.append({
                'object': obj,
                'channels': channels,
                'channel_order': channel_order
            })
            
        return obj

    def parse_motion(self):
        # Parse Frame Count
        line = self.lines[self._line_idx]
        if "Frames:" in line:
            # self.frame_count = int(line.split()[1]) # Not strictly needed, we just count the array
            self._line_idx += 1
            
        # Parse Frame Time
        line = self.lines[self._line_idx]
        if "Frame Time:" in line:
            self.frame_time = float(line.split()[-1])
            self._line_idx += 1
            
        # Parse Data
        while self._line_idx < len(self.lines):
            line = self.lines[self._line_idx]
            vals = [float(x) for x in line.split()]
            self.frames.append(vals)
            self._line_idx += 1