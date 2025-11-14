import glfw

def key_callback(window, key, scancode, action, mods):
    # Log when key is pressed or released
    if action == glfw.PRESS:
        print(f"Key pressed: {chr(key)}")
    elif action == glfw.RELEASE:
        print(f"Key released: {chr(key)}")
    elif action == glfw.REPEAT:
        print(f"Key repeated: {chr(key)}")