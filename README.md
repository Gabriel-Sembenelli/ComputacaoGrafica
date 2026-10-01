# ComputacaoGrafica

Disciplina de Computação Gráfica na UFABC

[Site do professor](http://professor.ufabc.edu.br/~mario.gazziro/cg/)

e-mail: `mario.gazziro@ufabc.edu.br`

## Aula 1

- 90% A
- 80% B
- 70% C
- 60% D
- <60% F

```
sudo apt install python-is-python3
sudo apt install python3-pip
python3 -m pip install moderngl --break-system-packages
python3 -m pip install pygame --break-system-packages
python 01_hello_world.py
pip install moderngl numpy objloader pillow pygame-ce pyglm glfw --break-system-packages
```

### Dúvidas e observações

> Qual a diferença do 03 e 04?

> Qual a diferença do 10, 11 e 12?

> O 13 brilha mais que o {10, 11, 12}

> O 14 fica 'chiado'

> O 15 tem fps, time_elapsed e posição do mouse

### Desafio de fluidsGL

This code is from the official NVIDIA CUDA "fluidsGL" sample. Because it relies on the CUDA Fast Fourier Transform library (CUFFT), OpenGL, and missing helper files like `fluidsGL_kernels.h` and `helper_cuda.h`, you cannot compile `defines.h` and `fluidsGL.cpp` in isolation.

Here is the easiest way to get it running:

1. **Install Prerequisites**: Ensure you have an NVIDIA GPU, the NVIDIA CUDA Toolkit, and FreeGLUT installed (e.g., `sudo apt install freeglut3-dev` on Linux).
2. **Download the Full Sample**: Clone the official NVIDIA CUDA Samples repository from GitHub to get the required helper files (`helper_gl.h`, `helper_cuda.h`, `fluidsGL_kernels.h`, and `fluidsGL_kernels.cu`).


3. **Compile**: Open a terminal, navigate to the `fluidsGL` directory within the downloaded samples, and run `make`.
4. **Execute**: Run the resulting binary by typing `./fluidsGL`.

If you manually gather all the missing headers and source files into a single directory, you can compile the simulation using the `nvcc` compiler:

```bash
nvcc fluidsGL.cpp fluidsGL_kernels.cu -o fluidsGL -lcufft -lGL -lGLU -lglut

```

Once running, you can click and drag with your mouse to interact with the fluid, press `r` to reset the simulation, or press `ESC` to exit.
