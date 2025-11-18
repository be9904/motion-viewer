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
    float diff = pow(max(dot(norm, lightDir), 0.0), 0.7);

    // --- 2-level cel shading ---
    float shade;
    if (diff > 0.4)
        shade = 1.0;      // bright
    else if (diff > 0.1)
        shade = 0.5;      // mid
    else
        shade = 0.1;      // dark

    vec3 result = shade * lightColor * objectColor;
    FragColor = vec4(result, 1.0);
}
