from random import gauss, randint
from math import sin, cos, pi

import pyglet
import pymunk


class Terrain(object):
    def __init__(self, batch, space, window, interval=100, mid_height=360, 
                 height_change=0.65, end_coordinate=30000, color_set='green',
                 group=None):
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
            verts = (coord1, coord2, (coord2[0], 0), (coord1[0]-25, 0))
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

    def update(self, x_offset=0, update_all=False):
        for i in range(len(self.terrain_shapes)):
            vertices = self.terrain_shapes[i].get_vertices()
            if -self.interval-60 < vertices[0][0]-x_offset < self.window.width+self.interval+60 or update_all:
                pyglet_coords = []
                for v in vertices:
                    x, y = v
                    pyglet_coords.extend((x-x_offset, y))
                self.terrain_primitives[i].vertices = pyglet_coords

class SymmetricTerrain(object):
    def __init__(self, batch, space, window, color_set='gray', group=None):
        if color_set == 'green':
            color1 = (78, 51, 0)*2 + (0, 145, 48)*2
            color2 = (78, 51, 0)*2 + (0, 78, 26)*2
        elif color_set == 'gray':
            color1 = (78, 51, 0)*2 + (128, 128, 128)*2
            color2 = (78, 51, 0)*2 + (80, 80, 80)*2
        self.batch = batch
        self.space = space
        self.window = window
        width = self.window.width

        self.terrain_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.terrain_body.position = (width//2, 0)
        self.terrain_shapes = []
        self.terrain_primitives = []
        interval = self.window.width//2

        height_change = randint(-15, 15)
        period = randint(100, 200)
        coords = []
        for i in range(-width//2, width//2+interval, interval):
            x, y = i, 135 + height_change*cos(i/period)
            coords.append((x, y))

        for i, coord in enumerate(list(zip(coords, coords[1:]))):
            coord1, coord2 = coord
            verts = (coord1, coord2, (coord2[0], 0), (coord1[0], 0))
            terrain_shape = pymunk.Poly(self.terrain_body, verts)
            terrain_shape.filter = pymunk.ShapeFilter(categories=0b0001000, 
                                                      mask=0b1100101)
            terrain_shape.elasticity = 0.9
            terrain_shape.friction = 0.95
            terrain_shape.collision_type = 6 if coord2[0] <= 0 else 7
            self.terrain_shapes.append(terrain_shape)

            self.terrain_primitives.append(self.batch.add_indexed(
                4, pyglet.gl.GL_TRIANGLES, group,
                [0, 1, 3, 1, 2, 3],
                ('v2f', (*coord1, *coord2, coord2[0], 0, coord1[0], 0)),
                ('c3B', color1 if i%2 == 0 else color2)
            ))
        self.space.add(*self.get_physical_object())
        self.update()

    def get_physical_object(self):
        return [self.terrain_body] + self.terrain_shapes

    def update(self):
        for i in range(len(self.terrain_shapes)):
            vertices = self.terrain_shapes[i].get_vertices()
            pyglet_coords = []
            for v in vertices:
                x, y = v
                pyglet_coords.extend((x+self.window.width//2, y))
            self.terrain_primitives[i].vertices = pyglet_coords