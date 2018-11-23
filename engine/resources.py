import pyglet


def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2

# Tell pyglet where to find the resources
pyglet.resource.path = ['../resources']
pyglet.resource.reindex()

images = []

# Load the three main resources and get them to draw centered
tank_body_img = pyglet.resource.image('tank_body_img.png')
images.append(tank_body_img)

tank_head_img = pyglet.resource.image('tank_head_img.png')
images.append(tank_head_img)

boxlife_img = pyglet.resource.image('boxlife_img.png')
images.append(boxlife_img)

boxlife_dead_img = pyglet.resource.image('boxlife_dead_img.png')
images.append(boxlife_dead_img)

wheel_img = pyglet.resource.image('wheel_img.png')
images.append(wheel_img)

thread_img = pyglet.resource.image('thread_img.png')
images.append(thread_img)

motorbike_chassis_img = pyglet.resource.image('motorbike_chassis_img.png')
images.append(motorbike_chassis_img)

mb_wheel_img = pyglet.resource.image('mb_wheel_img.png')
images.append(mb_wheel_img)

mb_holder_img = pyglet.resource.image('mb_holder_img.png')
images.append(mb_holder_img)

game1_button_img = pyglet.resource.image('game1_img.png')
images.append(game1_button_img)

game1_button_img_hover = pyglet.resource.image('game1_img_hover.png')
images.append(game1_button_img_hover)

game2_button_img = pyglet.resource.image('game2_img.png')
images.append(game2_button_img)

game2_button_img_hover = pyglet.resource.image('game2_img_hover.png')
images.append(game2_button_img_hover)

menu_button_img = pyglet.resource.image('menu_img.png')
images.append(menu_button_img)

gravity_button_img = pyglet.resource.image('gravity_img.png')
images.append(gravity_button_img)

restart_button_img = pyglet.resource.image('restart_button_img.png')
images.append(restart_button_img)

enter_button_img = pyglet.resource.image('enter_button_img.png')
images.append(enter_button_img)

enter_button_hover_img = pyglet.resource.image('enter_button_hover_img.png')
images.append(enter_button_hover_img)

circle_meter_img = pyglet.resource.image('circle_meter_img.png')
images.append(circle_meter_img)

pointer_img = pyglet.resource.image('pointer_img.png')
images.append(pointer_img)

finishflag_img = pyglet.resource.image('finishflag_img.png')
images.append(finishflag_img)

goal_meter_img = pyglet.resource.image('goal_meter_img.png')
images.append(goal_meter_img)

bg_goal_meter_img = pyglet.resource.image('bg_goal_meter_img.png')
images.append(bg_goal_meter_img)

for image in images:
    center_image(image)

# Load the engine_sfx without streaming
engine_sfx = pyglet.media.load('../resources/engine_sfx.wav', streaming=False)
