from random import gauss
from math import sin, pi

import pyglet
import pymunk


class Terrain(object):
    def __init__(self, batch, space, window, interval=100, mid_height=360, 
                 height_change=0.65, end_coordinate=30000, color_set='green',
                 group=None):
        self.offset = 0
        self.alive = True
        if color_set == 'green':
            color1 = (78, 51, 0)*2 + (0, 145, 48)*2
            color2 = (78, 51, 0)*2 + (0, 78, 26)*2
        elif color_set == 'gray':
            color1 = (78, 51, 0)*2 + (128, 128, 128)*2
            color2 = (78, 51, 0)*2 + (80, 80, 80)*2
        # color1 = (0, 145, 48)*2 + (78, 51, 0)*2
        # color2 = (0, 78, 26)*2 + (78, 51, 0)*2
        self.batch = batch
        self.space = space
        self.window = window
        self.interval = interval
        self.terrain_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.terrain_body.position = (0, 0)
        self.terrain_shapes = []
        self.terrain_primitives = []

        coords = []
        for i in range(0, end_coordinate+interval, interval):
            increasing_randomness = 70-60*sin((i/700)-(pi/2))*\
                                    gauss(0, height_change)
            x = i
            y = mid_height-60*sin(i/200) + increasing_randomness
            coords.append((x, y))

        for i, coord in enumerate(list(zip(coords, coords[1:]))):
            coord1, coord2 = coord
            verts = (coord1, coord2, (coord2[0], 0), (coord1[0]-30, 0))
            terrain_shape = pymunk.Poly(self.terrain_body, verts)
            terrain_shape.filter = pymunk.ShapeFilter(categories=0b0001000, 
                                                      mask=0b1110111)
            terrain_shape.elasticity = 0.4
            terrain_shape.friction = 0.85
            self.terrain_shapes.append(terrain_shape)

            self.terrain_primitives.append(self.batch.add_indexed(
                4, pyglet.gl.GL_TRIANGLES, group,
                [0, 1, 3, 1, 2, 3],
                ('v2f', (*coord1, *coord2, coord2[0], 0, coord1[0], 0)),
                ('c3B', color1 if i%2 == 0 else color2)
            ))
        self.space.add(*self.get_physical_object())

    def get_physical_object(self):
        return [self.terrain_body] + self.terrain_shapes

    def update(self, myb, parentb):
        while self.alive:
            myb.wait()
            for i in range(len(self.terrain_shapes)):
                vertices = self.terrain_shapes[i].get_vertices()
                if -self.interval-40 < vertices[0][0]-self.offset < self.window.width+self.interval+30:
                    pyglet_coords = []
                    for v in vertices:
                        x, y = v
                        pyglet_coords.extend((x-self.offset, y))
                    self.terrain_primitives[i].vertices = pyglet_coords
            parentb.wait()
