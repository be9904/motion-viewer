#version 330 core

// Inputs from vertex shader
in vec3 v_normal;
in vec3 v_world_pos;

// Outputs to framebuffer
out vec4 frag_color;

// Uniforms
uniform vec4 light_position;   // xyz = pos, w=0: directional
uniform vec3 light_color;
uniform float light_intensity;

void main()
{
    // Normalize the normal
    vec3 N = normalize(v_normal);

    // Compute light direction (from fragment to light)
    vec3 L = normalize(light_position.xyz - v_world_pos);

    // Lambertian diffuse term
    float NdotL = max(dot(N, L), 0.0);

    // Final color (white surface for example)
    vec3 base_color = vec3(1.0);

    // Diffuse lighting
    vec3 diffuse = base_color * light_color * (light_intensity * NdotL);

    frag_color = vec4(diffuse, 1.0);
}
