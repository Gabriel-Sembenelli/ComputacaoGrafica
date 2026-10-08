import sys

try :
    import glfw
    import moderngl
except ImportError as erro :
    sys.exit(f"FALHA: pacote ausente -> {erro}")

def erro_glfw(codigo, descricao):
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)

glfw.set_error_callback(erro_glfw)

if not glfw.init():
    sys.exit("FALHA : glfw nao inicializou")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
janela = glfw.create_window(800, 600, "Janela e contexto OpenGL", None, None)
if not janela:
    glfw.terminate()
    sys.exit("FALHA : não foi possível criar a janela")
glfw.make_context_current(janela)
ctx = moderngl.create_context()
print(f"GL_VERSION  : {ctx.info ['GL_VERSION']}")
print(f"GL_RENDERER : {ctx.info ['GL_RENDERER']}")
print(f"GL_VENDOR   : {ctx.info ['GL_VENDOR']}")
print(f"GL (codigo) : {ctx.version_code}")
print("\nESC ou feche a janela para sair.")

while not glfw.window_should_close(janela):
    if glfw.get_key(janela, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(janela, True)
    ctx.clear(1.0 , 1.0 , 1.0 , 1.0)
    glfw.swap_buffers(janela)
    glfw.poll_events()

glfw.terminate ()
print("Execucao finalizada." )
