from math import degrees
import pyglet
import pymunk
from . import resources

class PhysicalObject(object):
    def __init__(self, body, sprite, rotation_offset=0):
        self.body = body
        self.sprite = sprite
        self.rotation_offset = rotation_offset

    def update(self, x_offset=0):
        self.sprite.update(
            x=self.body.position.x - x_offset,
            y=self.body.position.y,
            rotation=-degrees(self.body.angle) + self.rotation_offset
        )

class GameBall(PhysicalObject):
    def __init__(self, batch, space, position, radius, group=None):
        mass = 0.1
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = position
        self.shape = pymunk.Circle(body, radius)
        self.shape.filter = pymunk.ShapeFilter(categories=0b0000100, mask=0b1101111)
        self.shape.elasticity = 1
        self.shape.friction = 0.9
        self.shape.collision_type = 5
        sprite = pyglet.sprite.Sprite(
            img=resources.vb_ball_img, 
            x=body.position.x, y=body.position.y, batch=batch, group=group)
        sprite.scale = (2*radius)/sprite.width
        super().__init__(body, sprite)
        self.space = space
        self.space.add(self.body, self.shape)

    def delete(self):
        self.space.remove(self.body, self.shape)
        self.sprite.delete()
