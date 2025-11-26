#version 330 core

// Inputs — per-vertex attributes
layout(location = 0) in vec3 position;   // local vertex position
layout(location = 1) in vec3 normal;     // local vertex normal

// Outputs — passed to fragment shader
out vec3 v_normal;       // normal in world space
out vec3 v_world_pos;    // vertex world position

// Uniforms
uniform mat4 model_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

void main()
{
    // Transform vertex into world space
    vec4 world_pos = model_matrix * vec4(position, 1.0);
    v_world_pos = world_pos.xyz;

    // Transform normal (no translation, keep only rotation+scale)
    v_normal = mat3(model_matrix) * normal;

    // Final clip space position
    gl_Position = projection_matrix * view_matrix * world_pos;
}
