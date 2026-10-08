# WebGL Water
# https://madebyevan.com/webgl-water/
# Copyright 2011 Evan Wallace
# Released under the MIT license

import moderngl
from light_gl import *


class Water:
    _vert_shader = """
    out vec2 coord;
    void main() {
        coord = gl_Vertex.xy * 0.5 + 0.5;
        gl_Position = vec4(gl_Vertex.xyz, 1.0);
    }
    """

    _drop_frag_shader = """
    const float PI = 3.141592653589793;
    uniform sampler2D texture_obj; // Renomeado para evitar conflito com palavra reservada
    uniform vec2 center;
    uniform float radius;
    uniform float strength;
    in vec2 coord;
    out vec4 frag_color;
    void main() {
        /* get vertex info */
        vec4 info = texture(texture_obj, coord);
        /* add the drop to the height */
        float drop = max(0.0, 1.0 - length(center * 0.5 + 0.5 - coord) / radius);
        drop = 0.5 - cos(drop * PI) * 0.5;
        info.r += drop * strength;
        frag_color = info;
    }
    """

    _update_frag_shader = """
    uniform sampler2D texture_obj; // Renomeado
    uniform vec2 delta;
    in vec2 coord;
    out vec4 frag_color;

    vec4 water_sample(vec2 coord, vec4 info) {
        return texture(texture_obj, coord);
    }

    void main() {
        /* get vertex info */
        vec4 info = water_sample(coord, vec4(0.5));
        
        /* calculate average neighbor height */
        vec2 dx = vec2(delta.x, 0.0);
        vec2 dy = vec2(0.0, delta.y);
        float average = (
            water_sample(coord - dx, info).r +
            water_sample(coord - dy, info).r +
            water_sample(coord + dx, info).r +
            water_sample(coord + dy, info).r
        ) * 0.25;
        
        /* change the velocity to move toward the average */
        info.g += (average - info.r) * 2.0;
        
        /* attenuate the velocity a little so waves do not last forever */
        info.g *= 0.995;
        
        /* move the vertex along the velocity */
        info.r += info.g;

        frag_color = vec4(info.rg, 0.0, 0.0);
    }
    """

    _normal_frag_shader = """
    uniform sampler2D texture_obj; // Renomeado
    uniform vec2 delta;
    in vec2 coord;
    out vec4 frag_color;
    void main() {
        /* get vertex info */
        vec4 info = texture(texture_obj, coord);
        
        /* update the normal */
        vec3 dx = vec3(delta.x, texture(texture_obj, vec2(coord.x + delta.x, coord.y)).r - info.r, 0.0);
        vec3 dy = vec3(0.0, texture(texture_obj, vec2(coord.x, coord.y + delta.y)).r - info.r, delta.y);
        info.ba = normalize(cross(dy, dx)).xz;
        
        frag_color = info;
    }
    """

    _sphere_frag_shader = """
    uniform sampler2D texture_obj; // Renomeado
    uniform vec3 oldCenter;
    uniform vec3 newCenter;
    uniform float radius;
    in vec2 coord;
    out vec4 frag_color;
    
    float volumeInSphere(vec3 center) {
      vec3 toCenter = vec3(coord.x * 2.0 - 1.0, 0.0, coord.y * 2.0 - 1.0) - center;
      float t = length(toCenter) / radius;
      float dy = exp(-pow(t * 1.5, 6.0));
      float ymin = min(0.0, center.y - dy);
      float ymax = min(max(0.0, center.y + dy), ymin + 2.0 * dy);
      return (ymax - ymin) * 0.1;
    }
    
    void main() {
      /* get vertex info */
      vec4 info = texture(texture_obj, coord);
      
      /* add the old volume */
      info.r += volumeInSphere(oldCenter);
      
      /* subtract the new volume */
      info.r -= volumeInSphere(newCenter);
      
      frag_color = info;
    }
    """

    def __init__(self, texture_size=(256, 256), ctx: moderngl.Context = None) -> None:
        self.ctx = ctx or None
        self.panel = MeshBuilder.panel().build(self.ctx)
        self.texture_a = RawTexture(
            texture_size, pixel_fmt="RGBA", ctx=self.ctx, dtype="f4")
        self.texture_b = RawTexture(
            texture_size, pixel_fmt="RGBA", ctx=self.ctx, dtype="f4")
        self.delta = glm.vec2(
            1.0 / texture_size[0], 1.0 / texture_size[1])
        self.drop_shader = Shader(
            Water._vert_shader, Water._drop_frag_shader, self.ctx)
        self.update_shader = Shader(
            Water._vert_shader, Water._update_frag_shader, self.ctx)
        self.normal_shader = Shader(
            Water._vert_shader, Water._normal_frag_shader, self.ctx)
        self.sphere_shader = Shader(
            Water._vert_shader, Water._sphere_frag_shader, self.ctx)

    def swap(self):
        temp_texture = self.texture_b
        self.texture_b = self.texture_a
        self.texture_a = temp_texture

    def add_drop(self, x: float, y: float, radius: float, strength: float):
        self.texture_b.draw_to(self.ctx)
        self.texture_a.use()
        self.drop_shader.draw_mesh(self.panel, uniforms={
            "center": glm.vec2(x, y),
            "radius": radius,
            "strength": strength
        })
        self.swap()

    def move_sphere(self, old_center, new_center, radius):
        self.texture_b.draw_to(self.ctx)
        self.texture_a.use()
        self.sphere_shader.draw_mesh(self.panel, uniforms={
            "oldCenter": old_center,
            "newCenter": new_center,
            "radius": radius
        })
        self.swap()

    def step_simulation(self):
        self.texture_b.draw_to(self.ctx)
        self.texture_a.use()
        self.update_shader.draw_mesh(self.panel, uniforms={
            "delta": self.delta
        })
        self.swap()
    
    def update_normals(self):
        self.texture_b.draw_to(self.ctx)
        self.texture_a.use()
        self.normal_shader.draw_mesh(self.panel, uniforms={
            "delta": self.delta
        })
        self.swap()
