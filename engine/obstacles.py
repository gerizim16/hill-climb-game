from random import randint, gauss, uniform
from math import sin, cos, pi

import pyglet
import pymunk


class Obstacles(object):
    def __init__(self, batch, space, window, end_coordinate=30000, radius_range=(10, 40), 
                 mass=1, frequency=125, amount=4, x_offset=0, min_height=380,
                 group=None):
        self.batch = batch
        self.space = space
        self.window = window
        color = (221, 139, 67) + (135, 85, 40) + (100, 40, 20)
        original_coords = [(round(cos(x*(pi/3)), 4), round(sin(x*(pi/3)), 4)) for x in range(6)]
        self.obstacle_bodies = []
        self.obstacle_shapes = []
        self.obstacle_primitives = []

        for i in range(0, end_coordinate+1, frequency):
            activated = True if -sin((i+1+x_offset)/500) > 0 else False
            if activated:
                for j in range(randint(0, amount)):
                    mid_radius = (radius_range[0]+radius_range[1])//2
                    radius = mid_radius + (mid_radius-radius_range[0])*(gauss(0, 0.2))

                    pymunk_coords = []
                    for k in range(6):
                        random_change = uniform(-radius/3, radius/3)
                        pymunk_coords.append(
                            (original_coords[k][0]*(radius+random_change), original_coords[k][1]*(radius+random_change)))

                    obstacle_moment = pymunk.moment_for_poly(mass, pymunk_coords)
                    obstacle_body = pymunk.Body(mass, obstacle_moment)
                    obstacle_body.position = i, min_height + j*80
                    obstacle_shape = pymunk.Poly(obstacle_body, pymunk_coords)
                    obstacle_shape.filter = pymunk.ShapeFilter(categories=0b0000100, mask=0b1111111)
                    obstacle_shape.elasticity = 0.7
                    obstacle_shape.friction = 0.9
                    self.obstacle_bodies.append(obstacle_body)
                    self.obstacle_shapes.append(obstacle_shape)

                    pyglet_coords = []
                    for coord in pymunk_coords:
                        pyglet_coords.extend(coord)

                    self.obstacle_primitives.append(self.batch.add_indexed(
                        6, pyglet.gl.GL_TRIANGLES, group,
                        [0, 1, 5, 1, 2, 5, 2, 4, 5, 2, 3, 4],
                        ('v2f', pyglet_coords),
                        ('c3B', color*2)
                    ))
        self.space.add(*self.get_physical_object())

    def get_physical_object(self):
        return self.obstacle_bodies + self.obstacle_shapes

    def update(self, x_offset=0):
        for i in range(len(self.obstacle_bodies)):
            if -60 < self.obstacle_bodies[i].position.x-x_offset < self.window.width + 60:
                pyglet_coords = []
                for v in self.obstacle_shapes[i].get_vertices():
                    x, y = v.rotated(self.obstacle_shapes[i].body.angle) + self.obstacle_shapes[i].body.position
                    pyglet_coords.extend((x-x_offset, y))
                self.obstacle_primitives[i].vertices = pyglet_coords
