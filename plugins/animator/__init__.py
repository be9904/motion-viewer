import time
from OpenGL.GL import glUseProgram

import core
from plugins.bvh import BVH
from plugins.joint import Joint

class Animator(core.Plugin):
    def __init__(self):
        super().__init__()
        # 1. Composition: The Animator owns the Loader
        self.loader = BVH()
        
        # 2. Playback State
        self.is_playing = True
        self.playback_speed = 1.0
        self.loop = True
        
        # 3. Timekeeping
        self.start_time = 0.0
        self.current_frame_index = 0
        self.accumulated_time = 0.0
        self.last_update_time = time.time()

    def assemble(self, import_data):
        # Allow main.py to inject a specific BVH file path if needed
        pass

    def init(self):
        # 1. Load the BVH File
        # (Hardcoded for demo, but ideally passed via SharedData or UI)
        try:
            print("Animator: Loading BVH...")
            self.loader.load_from_path("assets/a_001_1_1.bvh")
            self.start_time = time.time()
            self.last_update_time = time.time()
            print("Animator: Ready.")
        except FileNotFoundError:
            print("Animator Error: 'assets/walk.bvh' not found.")

    def update(self):
        if not self.loader.root_object or not self.loader.frames:
            return

        # 1. Time Management
        current_real_time = time.time()
        delta_time = current_real_time - self.last_update_time
        self.last_update_time = current_real_time

        if self.is_playing:
            # Accumulate time adjusted by speed
            self.accumulated_time += delta_time * self.playback_speed
            
            # Calculate frame index based on BVH's defined frame time
            # Frame = (Total Time / Time Per Frame)
            raw_frame = self.accumulated_time / self.loader.frame_time
            
            if self.loop:
                self.current_frame_index = int(raw_frame) % len(self.loader.frames)
            else:
                self.current_frame_index = min(int(raw_frame), len(self.loader.frames) - 1)

        # 2. Pose Application
        # We retrieve the specific frame of data
        frame_data = self.loader.frames[self.current_frame_index]
        data_ptr = 0

        # Iterate through the flattened list of animated nodes (created by Loader)
        for node in self.loader.animated_nodes:
            joint = node['object']
            
            # The Joint class handles the specific matrix math
            if isinstance(joint, Joint):
                data_ptr = joint.set_pose_from_frame(frame_data, data_ptr)

        # 3. Rendering
        # Fetch shared resources (Camera & Shader) from Core
        shader = core.SharedData.import_data("standard_shader")
        camera = core.SharedData.import_data("camera")

        if shader and camera:
            glUseProgram(shader.program)
            
            # Update Camera Uniforms
            shader.set_uniform_matrix4fv("view_matrix", camera.view)
            shader.set_uniform_matrix4fv("projection_matrix", camera.projection)
            
            # Draw the Skeleton Hierarchy
            # Calling draw() on the root automatically draws all children (Joints)
            # and their components (Bones/Lines)
            self.loader.root_object.draw(shader.program)

    def release(self):
        self.loader.release()
        self.loader = None

    # ---------------------------------------------
    # Controls (Can be hooked up to GUI or Keyboard)
    # ---------------------------------------------
    
    def play(self):
        self.is_playing = True
        self.last_update_time = time.time()

    def pause(self):
        self.is_playing = False

    def set_speed(self, speed):
        self.playback_speed = speed

    def reset(self):
        self.accumulated_time = 0.0
        self.current_frame_index = 0