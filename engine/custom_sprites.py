import pyglet
from . import resources


def mapFromTo(x, a, b, c, d):
    y=(x-a)/(b-a)*(d-c)+c
    return y

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
            x=x, y=y, batch=batch, group=group
        )

    def update(self, completion_percent):
        self.meter_sprite.update(x=self.start + self.distance*completion_percent)

class MeterSprite(object):
    def __init__(self, batch, position, scale=1, group=None):
        x, y = position
        self.motor_sprite_bg = pyglet.sprite.Sprite(
            img=resources.circle_meter_img,
            x=x, y=y, batch=batch, group=group)
        self.motor_sprite = pyglet.sprite.Sprite(img=resources.pointer_img, 
            x=x, y=y, batch=batch, group=group)
        self.motor_sprite.rotation = -25
        self.motor_sprite_bg.scale = 0.5*scale
        self.motor_sprite.scale = 0.5*scale

    def update(self, percent):
        self.motor_sprite.update(rotation=-25+230*percent)

class ParallaxBG(object):
    def __init__(self, batch, size, bg_index=0):
        self.window_width, self.window_height = size
        self.background_layers = list()
        self.past_offset = 0
        self.new_offset = 0
        for image_i, image in enumerate(resources.parallax_bgs[bg_index]):
            sprite_set = list()
            for i in range(2):
                scale = self.window_height/image.height
                x = image.width*scale*i
                sprite_set.append(
                    pyglet.sprite.Sprite(img=image, x=x, y=0, batch=batch,
                                         group=pyglet.graphics.OrderedGroup(image_i)
                ))
                sprite_set[i].update(scale=scale)
            self.background_layers.append(sprite_set)

    def update(self, offset=0):
        self.new_offset = offset
        for i, sprite_set in enumerate(self.background_layers[::-1], 2):
            sprite_set[0].x += (self.past_offset - self.new_offset)/i
            sprite_set[1].update(x=sprite_set[0].x+sprite_set[0].width)
            if sprite_set[0].x >= 0:
                sprite_set[1].update(x=sprite_set[0].x-sprite_set[0].width)
                sprite_set.reverse()
            elif sprite_set[1].x+sprite_set[1].width <= self.window_width:
                sprite_set[0].update(x=sprite_set[1].x+sprite_set[1].width)
                sprite_set.reverse()
        self.past_offset = offset

class BallIndicator(object):
    def __init__(self, batch, window, group=None):
        self.height = window.height
        self.max_height = self.height + 400
        self.length = 70
        self.batch = batch
        self.opacity = 0
        self.sprite = self.batch.add_indexed(
            4, pyglet.gl.GL_TRIANGLES, group,
            [0, 1, 3, 1, 2, 3],
            ('v2f', (0, 0, 0, 1, 1, 1, 1, 0)),
            ('c4B', (0, 0, 0, 0)*4)
        )

    def update(self, x, height):
        if height > self.height:
            self.opacity = 255
            width = mapFromTo(height, self.height, self.max_height, 0, self.length)
            verts = (
                x-width, self.height,
                x+width, self.height,
                x+width, self.height-20,
                x-width, self.height-20,
            )
            color = (int(mapFromTo(height, self.height, self.max_height, 255, 0)), int(mapFromTo(height, self.height, self.max_height, 0, 255)), 0, self.opacity)*4
            self.sprite.vertices = verts
        else:
            self.opacity = 0
            color = (255, 255, 255, self.opacity)*4
        self.sprite.colors = color
