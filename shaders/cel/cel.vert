#version 410 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

uniform mat4 model_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;

out vec4 fragPos;
out vec3 fragNormal;

void main() {
    fragPos = model * vec4(position, 1.0);
    fragNormal = mat3(transpose(inverse(model))) * normal;
    gl_Position = projection * view * fragPos;
}