import pyglet
from . import resources

class GoalSprite(object):
    def __init__(self, batch, position):
        x, y = position
        self.distance = resources.bg_goal_meter_img.width - resources.goal_meter_img.width + 40
        self.start = x - self.distance/2
        self.meter_sprite = pyglet.sprite.Sprite(
            img=resources.goal_meter_img, 
            x=self.start, y=y, batch=batch
        )

        self.bg_sprite = pyglet.sprite.Sprite(
            img=resources.bg_goal_meter_img,
            x=x, y=y, batch=batch
        )

    def update(self, completion_percent):
        self.meter_sprite.update(x=self.start + self.distance*completion_percent)
