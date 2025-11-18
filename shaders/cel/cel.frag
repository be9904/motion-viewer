#version 410 core
in vec3 fragNormal;
in vec3 fragPos;

out vec4 FragColor;

uniform vec3 lightPos;
uniform vec3 lightColor;
uniform vec3 objectColor;

void main() {
    vec3 norm = normalize(fragNormal);
    vec3 lightDir = normalize(lightPos - fragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 result = diff * lightColor * objectColor;
    FragColor = vec4(result, 1.0);
}