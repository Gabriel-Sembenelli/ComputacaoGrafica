"""
A primeira malha 3D : ler um arquivo OFF e por o modelo dentro da tela .
Nenhuma camera , nenhuma projecao : os vertices vao direto para o NDC.Como o
modelo do arquivo raramente cabe no cubo canonico , a CPU o encolhe e o
centraliza -- REESCREVENDO as coordenadas.A tecla N desliga essa reescrita , e
e por causa do que se ve entao que o proximo capitulo existe.
Executar : python 10_malha_off.py [ arquivo.off ]
Teclas : N normaliza ou nao | W aramado | C descarte de faces | ESC sai
"""
import sys
from pathlib import Path
import glfw
import moderngl
import numpy as np

AQUI = Path(__file__).parent
SHADERS = AQUI / "shaders"
PADRAO = AQUI / "off" / "torus.off"

LADO = 700
FUNDO = (0.10 , 0.11 , 0.13 , 1.0)
FOLGA = 0.9 # raio da esfera , no NDC , em que o modelo e encaixado

def ler_off( caminho ) :
    """Le um OFF de faces triangulares e devolve(vertices , indices ) .
    O formato inteiro sao tres blocos : a palavra OFF , uma linha com as
    contagens , e depois as coordenadas seguidas das faces.Cada face comeca
    com o numero de lados -- aqui sempre 3."""
    campos = []
    for linha in Path(caminho ).read_text(encoding ="utf-8").splitlines () :
        linha = linha.split ("#") [0]. strip () # comentario ate o fim da linha
        if linha :
            campos.extend(linha.split () )
    if campos [0]. upper () !="OFF":
        raise ValueError(f"{caminho}: nao comeca com OFF")
    
    n_vertices , n_faces = int(campos [1]) , int(campos [2])
    # campos [3] e o numero de arestas , que o formato permite deixar em zero .
    p = 4
    
    vertices = np.array(campos [ p : p + 3 * n_vertices ] ,
                        dtype ='f4').reshape(n_vertices , 3)
    p += 3 * n_vertices
    
    indices = np.empty (( n_faces , 3) , dtype ='u4')
    for i in range(n_faces ) :
        lados = int(campos [ p ])
        if lados != 3:
            raise ValueError(f"{caminho}: face {i} tem {lados} lados ;"
                            "este leitor so aceita triangulos")
        indices [ i ] = campos [ p + 1: p + 4]
        p += 1 + lados
    return vertices , indices

def esfera(vertices ) :
    """Esfera envolvente : centro da caixa alinhada aos eixos e distancia ate
    o vertice mais afastado dele ."""
    minimo , maximo = vertices.min(axis =0) , vertices.max(axis =0)
    centro = 0.5 *(minimo + maximo )
    raio = float(np.linalg.norm(vertices - centro , axis =1).max () )
    return minimo , maximo , centro , raio

def encaixar(vertices , centro , raio ) :
    """Leva o centro para a origem e reduz a esfera ao raio FOLGA .
    Todo vertice fica a no maximo FOLGA da origem , logo dentro do cubo
    canonico -- e continua dentro se o modelo for girado em torno dela .
    """
    return (( vertices - centro ) *(FOLGA / raio ) ).astype ('f4')

caminho = Path(sys.argv [1]) if len(sys.argv ) > 1 else PADRAO
if not caminho.exists () :
    sys.exit(f"FALHA : nao encontrei {caminho}")

posicoes , faces = ler_off( caminho )
minimo , maximo , centro , raio = esfera(posicoes )
posicoes_encaixadas = encaixar(posicoes , centro , raio )

print(f"arquivo : {caminho.name}")
print(f"vertices : {len(posicoes )} faces : {len(faces )}")
print(f"caixa : {minimo} ate {maximo}")
print(f"centro : {centro}")
print(f"raio : {raio :.4f}")

def erro_glfw(codigo , descricao ) :
    """Substitui o aviso padrao do pyGLFW : imprime codigo e descricao de
    qualquer erro do GLFW em stderr ."""
    print(f"GLFW [{codigo}]: {descricao}", file = sys.stderr )

glfw.set_error_callback(erro_glfw ) # antes de glfw.init () , de proposito

if not glfw.init () :
    sys.exit ("FALHA : glfw nao inicializou")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR , 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR , 0)
glfw.window_hint(glfw.OPENGL_PROFILE , glfw.OPENGL_CORE_PROFILE )
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT , glfw.TRUE )
# Sem a dica acima , o macOS recusa qualquer contexto 3.2+ e
# create_window devolve None.E inofensiva no Windows e no Linux .
glfw.window_hint(glfw.SAMPLES , 4)
glfw.window_hint(glfw.RESIZABLE , False )

janela = glfw.create_window(LADO , LADO ,"Malha OFF", None , None )
if not janela :
    glfw.terminate ()
    sys.exit ("FALHA : nao foi possivel criar a janela")

glfw.make_context_current(janela )
glfw.swap_interval (1)
ctx = moderngl.create_context ()

# A NOVIDADE DO CAPITULO.Ate aqui a cena era plana e a ordem do desenho
# resolvia a oclusao.Com o teste de profundidade , quem esta na frente ganha .
# Liga - se uma vez : o estado vale ate ser desligado .
ctx.enable(moderngl.DEPTH_TEST )

prog = ctx.program (
    vertex_shader =( SHADERS /"profundidade.vert").read_text(encoding ="utf-8") ,
    fragment_shader =( SHADERS /"profundidade.frag").read_text(encoding ="utf-8") ,
)

# Um VBO por versao dos vertices : as duas convivem na VRAM e a tecla N so
# troca qual VAO e desenhado.Nada e recalculado durante o laco .
vbo_cru = ctx.buffer(posicoes.astype ('f4').tobytes () )
vbo_encaixado = ctx.buffer(posicoes_encaixadas.tobytes () )
ebo = ctx.buffer(faces.tobytes () )

vao_cru = ctx.vertex_array (
    prog , [( vbo_cru ,'3f','vPosition') ] , index_buffer = ebo )
vao_encaixado = ctx.vertex_array (
    prog , [( vbo_encaixado ,'3f','vPosition') ] , index_buffer = ebo )

normalizado = True
aramado = False
descartar = False

def tecla(window , key , scancode , action , mods ) :
    global normalizado , aramado , descartar
    if action != glfw.PRESS :
        return
    if key == glfw.KEY_ESCAPE :
        glfw.set_window_should_close(window , True )
    elif key == glfw.KEY_N :
        normalizado = not normalizado
    elif key == glfw.KEY_W :
        aramado = not aramado
    elif key == glfw.KEY_C :
        descartar = not descartar

glfw.set_key_callback(janela , tecla )

print ("\ nN alterna o encaixe | W aramado | C descarte de faces | ESC sai")

while not glfw.window_should_close(janela ) :
    # O clear do moderngl sempre limpa cor e profundidade , como
    # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT ) ; a profundidade
    # volta a 1.0 , o valor mais distante .
    ctx.clear (* FUNDO )
    if descartar :
        ctx.enable(moderngl.CULL_FACE )
    else :
        ctx.disable(moderngl.CULL_FACE )
    ctx.wireframe = aramado
    ( vao_encaixado if normalizado else vao_cru ).render(moderngl.TRIANGLES )
    glfw.swap_buffers(janela )
    glfw.poll_events ()
    
    glfw.set_window_title (
        janela ,
        f"{caminho.name} - {'encaixado'if normalizado else'CRU'}"
        f"{'- aramado'if aramado else''}"
        f"{'- descarte'if descartar else''}")

for recurso in(vao_cru , vao_encaixado , ebo , vbo_cru , vbo_encaixado , prog ) :
    recurso.release ()

glfw.terminate ()
print ("Execucao finalizada .")
