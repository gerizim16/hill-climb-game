import pyglet

print('Loading resources')

def center_image(image):
    """Sets an image's anchor point to its center"""
    image.anchor_x = image.width / 2
    image.anchor_y = image.height / 2

# Tell pyglet where to find the resources
pyglet.resource.path = ['./resources', './resources/backgrounds']
pyglet.resource.reindex()

images = list()

# Load the three main resources and get them to draw centered
tank_body_img = pyglet.resource.image('tank_body.png')
images.append(tank_body_img)

tank_head_img = pyglet.resource.image('tank_head.png')
images.append(tank_head_img)

boxlife_img = pyglet.resource.image('boxlife.png')
images.append(boxlife_img)

boxlife_dead_img = pyglet.resource.image('boxlife_dead.png')
images.append(boxlife_dead_img)

wheel_img = pyglet.resource.image('wheel.png')
images.append(wheel_img)

thread_img = pyglet.resource.image('thread.png')
images.append(thread_img)

motorbike_chassis_img = pyglet.resource.image('motorbike_chassis.png')
images.append(motorbike_chassis_img)

mb_wheel_img = pyglet.resource.image('mb_wheel.png')
images.append(mb_wheel_img)

mb_holder_img = pyglet.resource.image('mb_holder.png')
images.append(mb_holder_img)

vbv_chassis_img = pyglet.resource.image('vbv_chassis.png')
images.append(vbv_chassis_img)

vbv_wheels_img = pyglet.resource.image('vbv_wheels.png')
images.append(vbv_wheels_img)

vbv_platform_img = pyglet.resource.image('vbv_platform.png')
images.append(vbv_platform_img)

vb_net_img = pyglet.resource.image('vb_net.png')
images.append(vb_net_img)

vb_ball_img = pyglet.resource.image('vb_ball.png')
images.append(vb_ball_img)

game1_button_img = pyglet.resource.image('game1.png')
images.append(game1_button_img)

game1_button_hover_img = pyglet.resource.image('game1_hover.png')
images.append(game1_button_hover_img)

game2_button_img = pyglet.resource.image('game2.png')
images.append(game2_button_img)

game2_button_hover_img = pyglet.resource.image('game2_hover.png')
images.append(game2_button_hover_img)

game3_button_img = pyglet.resource.image('game3.png')
images.append(game3_button_img)

game3_button_hover_img = pyglet.resource.image('game3_hover.png')
images.append(game3_button_hover_img)

game1_hs_button_img = pyglet.resource.image('game1_hs.png')
images.append(game1_hs_button_img)

game1_hs_button_hover_img = pyglet.resource.image('game1_hs_hover.png')
images.append(game1_hs_button_hover_img)

game2_hs_button_img = pyglet.resource.image('game2_hs.png')
images.append(game2_hs_button_img)

game2_hs_button_hover_img = pyglet.resource.image('game2_hs_hover.png')
images.append(game2_hs_button_hover_img)

menu_button_img = pyglet.resource.image('menu.png')
images.append(menu_button_img)

gravity_button_img = pyglet.resource.image('gravity.png')
images.append(gravity_button_img)

fullscreen_button_img = pyglet.resource.image('fullscreen.png')
images.append(fullscreen_button_img)

restart_button_img = pyglet.resource.image('restart_button.png')
images.append(restart_button_img)

enter_button_img = pyglet.resource.image('enter_button.png')
images.append(enter_button_img)

enter_button_hover_img = pyglet.resource.image('enter_button_hover.png')
images.append(enter_button_hover_img)

circle_meter_img = pyglet.resource.image('circle_meter.png')
images.append(circle_meter_img)

pointer_img = pyglet.resource.image('pointer.png')
images.append(pointer_img)

finishflag_img = pyglet.resource.image('finishflag.png')
images.append(finishflag_img)

goal_meter_img = pyglet.resource.image('goal_meter.png')
images.append(goal_meter_img)

bg_goal_meter_img = pyglet.resource.image('bg_goal_meter.png')
images.append(bg_goal_meter_img)

background_img = pyglet.resource.image('background.png')
images.append(background_img)

for image in images:
    center_image(image)

# load backgrounds
parallax_bgs = list()
layer_counts = (3, 2, 2, 2, 3, 4)
for bg_i, layer_count in enumerate(layer_counts):
    bg_set = list()
    for layer_i in range(layer_count):
        bg_set.append(pyglet.resource.image('{}layer_{}.png'.format(bg_i, layer_i)))
    parallax_bgs.append(tuple(bg_set))
parallax_bgs = tuple(parallax_bgs)

# Load sfx without streaming
engine_sfx = pyglet.media.load('./resources/engine_sfx.wav', streaming=False)
bg_music = pyglet.media.load('./resources/bg_music.wav', streaming=False)

print('Resource loading successful')
