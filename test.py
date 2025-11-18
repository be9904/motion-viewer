import glfw
from OpenGL.GL import glGetString, GL_VERSION, GL_SHADING_LANGUAGE_VERSION

# Initialize GLFW
if not glfw.init():
    raise Exception("GLFW can't be initialized")

# Create a hidden window (we just need a context)
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
window = glfw.create_window(640, 480, "Temp", None, None)
glfw.make_context_current(window)

# Now you can query OpenGL
version = glGetString(GL_VERSION)
glsl_version = glGetString(GL_SHADING_LANGUAGE_VERSION)

print("OpenGL version:", version.decode())
print("GLSL version:", glsl_version.decode())

# Clean up
glfw.terminate()
