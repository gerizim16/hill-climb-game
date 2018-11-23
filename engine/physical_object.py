from math import degrees


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
