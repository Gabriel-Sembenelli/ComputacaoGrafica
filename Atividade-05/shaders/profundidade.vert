# version 400 core

// Sem camera e sem projecao ainda : o modelo vai direto para NDC , e a
// unica coisa que a CPU faz com ele e caber dentro do cubo canonico .
// A partir do proximo capitulo isto vira model * view * projection .

layout(location = 0) in vec4 vPosition;

out vec4 v2fcolor;

void main() {
    gl_Position = vPosition;
    // z no NDC vai de -1 ( perto ) a 1 ( longe ) . Mapeado para [0 ,1] , vira
    // um tom de cinza : claro atras , escuro na frente .
    float cinza = (vPosition.z + 1.0) * 0.5;
    v2fcolor = vec4(cinza, cinza, cinza, 1.0);
}