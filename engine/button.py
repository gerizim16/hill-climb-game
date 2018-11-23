from math import degrees

import pymunk
import pyglet


class Button(pymunk.Body):
    def __init__(self, batch, id, position, img, dimensions, 
            body_type=pymunk.Body.DYNAMIC, sensor=False, 
            group=pyglet.graphics.OrderedGroup(2)):
        super().__init__(1)
        self.COLLTYPE_BUTTON = 3
        self.id = id
        self.position = position
        self.body_type = body_type
        self.update_rotate = True
        if isinstance(dimensions, tuple) or isinstance(dimensions, list):
            self.moment = pymunk.moment_for_box(self.mass, dimensions)
            self.button_shape = pymunk.Poly.create_box(self, dimensions)
        elif isinstance(dimensions, int) or isinstance(dimensions, float):
            self.moment = pymunk.moment_for_circle(self.mass, 0, dimensions)
            self.button_shape = pymunk.Circle(self, dimensions)
        self.button_shape.sensor = sensor
        self.button_shape.filter = pymunk.ShapeFilter(categories=0b0000001, mask=0b1111111)
        self.button_shape.elasticity = 1
        self.button_shape.friction = 0.8
        self.button_shape.collision_type = self.COLLTYPE_BUTTON
        self.button_shape.id = id
        self.sprite = pyglet.sprite.Sprite(img, x=self.position.x, y=self.position.y,
            batch=batch, group=group)
    
    def update(self, x_offset=0):
        if self.update_rotate:
            self.sprite.update(
                x=self.position.x - x_offset,
                y=self.position.y,
                rotation=-degrees(self.angle)
            )
        else:
            self.sprite.update(
                x=self.position.x - x_offset,
                y=self.position.y
            )

    def get_physical_object(self):
        return (self,) + (self.button_shape,)
