import pyglet
from . import resources

class GoalSprite(object):
    def __init__(self, batch, position, group=None):
        x, y = position
        self.distance = resources.bg_goal_meter_img.width - resources.goal_meter_img.width + 40
        self.start = x - self.distance/2
        self.meter_sprite = pyglet.sprite.Sprite(
            img=resources.goal_meter_img, 
            x=self.start, y=y, batch=batch,
            group=group
        )

        self.bg_sprite = pyglet.sprite.Sprite(
            img=resources.bg_goal_meter_img,
            x=x, y=y, batch=batch
        )

    def update(self, completion_percent):
        self.meter_sprite.update(x=self.start + self.distance*completion_percent)

class MeterSprite(object):
    def __init__(self, batch, position, group=None):
        x, y = position
        self.motor_sprite_bg = pyglet.sprite.Sprite(
            img=resources.circle_meter_img,
            x=x, y=y, batch=batch, group=group)
        self.motor_sprite = pyglet.sprite.Sprite(img=resources.pointer_img, 
            x=x, y=y, batch=batch, group=group)
        self.motor_sprite.rotation = -25
        self.motor_sprite_bg.scale = 0.5
        self.motor_sprite.scale = 0.5

    def update(self, percent):
        self.motor_sprite.update(rotation=-25+230*percent)
