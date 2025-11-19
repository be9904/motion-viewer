#version 410 core
in vec4 fragPos;
in vec3 fragNormal;

out vec4 FragColor;

uniform mat4 view;
uniform vec4 lightPos;
uniform vec4 lightColor;
uniform vec4 objectColor;

void main() {
    vec3 norm = normalize(fragNormal);
    vec4 lightDir = normalize(view * lightPos - fragPos);
    float diff = pow(max(dot(norm, lightDir.xyz), 0.0), 0.7);

    // --- 2-level cel shading ---
    float shade;
    if (diff > 0.2)
        shade = 1.0;      // bright
    else if (diff > 0.01)
        shade = 0.5;      // mid
    else
        shade = 0.1;      // dark

    vec3 result = shade * lightColor.rgb * objectColor.rgb;
    FragColor = vec4(result, 1.0);
}
