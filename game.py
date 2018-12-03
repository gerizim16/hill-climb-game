from string import whitespace
from random import choice, randrange
from math import pi

# third party modules
import pyglet
from pyglet.window import key
import pymunk
from pymunk.pyglet_util import DrawOptions

# own modules
import engine.resources as resources
from engine.player import Tank, MotorBike, VbVehicle
from engine.terrain import Terrain, SymmetricTerrain
from engine.obstacles import Obstacles
from engine.button import Button
from engine.text_input import TextInput
from engine.hs_handling import get_highscores, add_highscore
from engine.scrolling_text import ScrollingText
from engine.custom_sprites import GoalSprite, MeterSprite, ParallaxBG, BallIndicator
from engine.sound_loop import SoundLoop
from engine.physical_object import GameBall

# categories: body, wheels, tank threads/vbboundery, 
#             floor, obstacles, tank boxlives, 
#             buttons

# collision: COLLTYPE_DEFAULT = 0
#            COLLTYPE_BOXLIFE = 1
#            COLLTYPE_SENSOR = 2
#            COLLTYPE_BUTTON = 3
#            COLLTYPE_MOUSE = 4
#            COLLTYPE_VB_BALL = 5
#            COLLTYPE_VB_PLAYER1 = 6
#            COLLTYPE_VB_PLAYER2 = 7
#            COLLTYPE_VB_PLAYER1_PLATFORM = 8
#            COLLTYPE_VB_PLAYER2_PLATFORM = 9

class Window(pyglet.window.Window):
    def __init__(self, width, height, caption='', resizeable=False):
        super().__init__(width, height, caption, resizeable)
        self.main_batch = pyglet.graphics.Batch()
        self.space = pymunk.Space()
        # self.space = pymunk.Space(threaded=True) # only for non windows os
        # self.space.threads = 4 # only for non windows os
        self.space.gravity = 0, -900

        self.activated_mode = Menu(self.main_batch, self.space, self)
        self.change_mode = None

        self.options = DrawOptions() # debugging
        # self.options.flags = pymunk.SpaceDebugDrawOptions.DRAW_SHAPES # debugging
        self.fps_display = pyglet.clock.ClockDisplay(color=(1,1,1,1)) # debugging

        # bg music ############################################################
        self.bg_music = SoundLoop(resources.bg_music)
        self.bg_music.play()
        #######################################################################

        pyglet.clock.schedule_interval(self.update, 1/60.0)

    def on_draw(self):
        # self.clear()
        # self.space.debug_draw(self.options) # debugging
        self.main_batch.draw()
        self.fps_display.draw() # debugging

    def update(self, dt):
        dt = 1/60.0
        self.space.step(dt) # update physics               # pymunk
        self.activated_mode.update() # update draws/camera # pyglet
        new_mode = self.activated_mode.change_to
        if new_mode:
            args_to_pass = self.activated_mode.args
            kwargs_to_pass = self.activated_mode.kwargs
            print('ID: {} | args: {} | kwargs: {}'.format(new_mode, args_to_pass, kwargs_to_pass))
            # delete current gamestate instance
            del self.activated_mode
            # remove objects in pymunk space
            self.space.remove(
                *self.space.bodies, 
                *self.space.shapes, 
                *self.space.constraints
            )
            del self.space
            self.space = pymunk.Space()
            # delete pyglet main batch
            del self.main_batch
            # create fresh pyglet main batch
            self.main_batch = pyglet.graphics.Batch()
            # remove handlers from pyglet window
            self.pop_handlers()
            # create new gamestate instance
            if new_mode == Game1.id:
                self.bg_music.volume = 0.1
                self.activated_mode = Game1(self.main_batch, self.space, self)
            if new_mode == Game2.id:
                self.bg_music.volume = 0.1
                self.activated_mode = Game2(self.main_batch, self.space, self)
            if new_mode == Game3.id:
                self.bg_music.volume = 0.6
                self.activated_mode = Game3(self.main_batch, self.space, self)
            elif new_mode == Menu.id:
                self.bg_music.volume = 0.6
                self.activated_mode = Menu(self.main_batch, self.space, self)
            elif new_mode == Endgame.id:
                self.bg_music.volume = 0.6
                self.activated_mode = Endgame(self.main_batch, self.space, self, *args_to_pass, **kwargs_to_pass)
            elif new_mode == HighScore.id:
                self.bg_music.volume = 0.6
                self.activated_mode = HighScore(self.main_batch, self.space, self, *args_to_pass, **kwargs_to_pass)

    def on_mouse_press(self, x, y, button, modifier):
        print('Mouse pressed:', x, y, button, modifier)

# MENU AND GAME MODES #########################################################
class GameState(object):
    id = 0
    def __init__(self, batch, space, window, mouse_hover=False, bounded=False):
        self.COLLTYPE_DEFAULT = 0
        self.COLLTYPE_BOXLIFE = 1
        self.COLLTYPE_SENSOR = 2
        self.COLLTYPE_BUTTON = 3
        self.COLLTYPE_MOUSE = 4
        self.COLLTYPE_VB_BALL = 5
        self.COLLTYPE_VB_PLAYER1 = 6
        self.COLLTYPE_VB_PLAYER2 = 7

        self.back = pyglet.graphics.OrderedGroup(10)
        self.background = pyglet.graphics.OrderedGroup(11)
        self.midground = pyglet.graphics.OrderedGroup(12)
        self.foreground = pyglet.graphics.OrderedGroup(13)
        self.front = pyglet.graphics.OrderedGroup(14)

        self.buttons = pymunk.ShapeFilter(mask=0b0000001)

        self.change_to = False
        self.args = list()
        self.kwargs = dict()
        self.batch = batch
        self.space = space
        self.window = window

        self.space.gravity = 0, -900

        self.event_handlers = []

        if bounded:
            # create window physical bounds ###################################
            bounds_shapes = []
            bounds_body = pymunk.Body(body_type=pymunk.Body.STATIC)
            bounds_body.position = (0, 0)
            bounds_filter = pymunk.ShapeFilter(categories=0b0001000, mask=0b1110111)
            left_bound_s = pymunk.Segment(bounds_body, 
                                        (-20, 0), (-20, self.window.height), 20)
            right_bound_s = pymunk.Segment(bounds_body, 
                                        (self.window.width+20, 0), 
                                        (self.window.width+20, self.window.height), 20)
            upper_bound_s = pymunk.Segment(bounds_body, 
                                        (self.window.width, self.window.height+20), 
                                        (0, self.window.height+20), 20)
            bounds_shapes.extend((left_bound_s, right_bound_s, upper_bound_s))
            for shape in bounds_shapes:
                shape.friction = 0.8
                shape.elasticity = 1
                shape.filter = bounds_filter
            ###################################################################
            self.space.add(bounds_body, *bounds_shapes)

        if mouse_hover:
            # mouse physical sensor ###########################################
            self.mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
            mouse_shape = pymunk.Circle(self.mouse_body, 1)
            mouse_shape.sensor = True
            mouse_shape.collision_type = self.COLLTYPE_MOUSE
            mouse_shape.filter = pymunk.ShapeFilter(categories=0b1000000)
            self.space.add(mouse_shape)
            self.space.add_collision_handler(
                self.COLLTYPE_BUTTON, self.COLLTYPE_MOUSE).begin = self.on_mouse_hover
            self.space.add_collision_handler(
                self.COLLTYPE_BUTTON, self.COLLTYPE_MOUSE).separate =\
                self.on_mouse_unhover
            ###################################################################

            self.event_handlers.append(self.on_mouse_motion)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_body.position = x, y
        # print(x, y)

    def on_mouse_hover(self, arbiter, space, data):
        pass
        return True

    def on_mouse_unhover(self, arbiter, space, data):
        pass
###############################################################################
class Menu(GameState):
    id = 1
    def __init__(self, batch, space, window):
        super().__init__(batch, space, window, mouse_hover=True, bounded=True)
        self.changing_gravity = False
        self.adder = [5, 5]
        self.time = 0
        self.bg = pyglet.sprite.Sprite(
            img=resources.background_img,
            x=self.window.width//2, y=self.window.height//2+100, batch=self.batch,
            group=self.midground
        )
        self.event_handlers.append(self.on_mouse_press)
        # objects #############################################################
        if choice((1, 2)) == 1:
            self.player = Tank(self.batch, self.space, self.window,
                               (self.window.width//2-450, 620), side='left',
                               group=self.background)
        else:
            self.player = MotorBike(self.batch, self.space, self.window,
                                    (self.window.width//2-450, 620),
                                    group=self.background)
        self.event_handlers.extend(self.player.event_handlers)
        self.terrain = Terrain(self.batch, self.space, self.window,
                                mid_height=150, end_coordinate=self.window.width+200,
                                color_set=choice(('green', 'gray')),
                                group=self.background)
        self.obstacles = Obstacles(self.batch, self.space, self.window,
            end_coordinate=self.window.width, frequency=40,
            amount=2, x_offset=1600, group=self.back)
        # buttons #############################################################
        self.game1_button = Button(self.batch, self.space, 'game1_button', 
            (self.window.width//2-250, 700), resources.game1_button_img, 60)
        self.game2_button = Button(self.batch, self.space, 'game2_button', 
            (self.window.width//2-100, 700), resources.game2_button_img, 60)
        self.game3_button = Button(self.batch, self.space, 'game3_button', 
            (self.window.width//2+50, 700), resources.game3_button_img, 60)
        self.game1_hs_button = Button(self.batch, self.space, 'game1_hs_button', 
            (self.window.width//2+200, 700), resources.game1_hs_button_img, 60)
        self.game2_hs_button = Button(self.batch, self.space, 'game2_hs_button', 
            (self.window.width//2+350, 700), resources.game2_hs_button_img, 60)
        self.gravity_button = Button(self.batch, self.space, 'gravity_button', 
            (self.window.width//2+450, 700), resources.gravity_button_img, 30)
        self.fullscreen_button = Button(self.batch, self.space, 'fullscreen_button', 
            (self.window.width//2+550, 700), resources.fullscreen_button_img, 60)
        #######################################################################
        self.window.push_handlers(*self.event_handlers)
        # sound fx ############################################################
        self.player.engine_sound.volume = 0.6
        self.parallax = ParallaxBG(self.batch, self.window.get_size(), randrange(6))

    def on_mouse_hover(self, arbiter, space, data):
        button_shape, mouse_shape = arbiter.shapes
        if button_shape.id == self.game1_button.id:
            self.game1_button.update_rotate = False
            self.game1_button.sprite.rotation = 0
            self.game1_button.sprite.image = resources.game1_button_hover_img
            self.game1_button.sprite.group = self.front
        elif button_shape.id == self.game2_button.id:
            self.game2_button.update_rotate = False
            self.game2_button.sprite.rotation = 0
            self.game2_button.sprite.image = resources.game2_button_hover_img
            self.game2_button.sprite.group = self.front
        elif button_shape.id == self.game3_button.id:
            self.game3_button.update_rotate = False
            self.game3_button.sprite.rotation = 0
            self.game3_button.sprite.image = resources.game3_button_hover_img
            self.game3_button.sprite.group = self.front
        elif button_shape.id == self.game1_hs_button.id:
            self.game1_hs_button.update_rotate = False
            self.game1_hs_button.sprite.rotation = 0
            self.game1_hs_button.sprite.image = resources.game1_hs_button_hover_img
            self.game1_hs_button.sprite.group = self.front
        elif button_shape.id == self.game2_hs_button.id:
            self.game2_hs_button.update_rotate = False
            self.game2_hs_button.sprite.rotation = 0
            self.game2_hs_button.sprite.image = resources.game2_hs_button_hover_img
            self.game2_hs_button.sprite.group = self.front
        return True

    def on_mouse_unhover(self, arbiter, space, data):
        button_shape, mouse_shape = arbiter.shapes
        if button_shape.id == self.game1_button.id:
            self.game1_button.update_rotate = True
            self.game1_button.sprite.image = resources.game1_button_img
            self.game1_button.sprite.group = self.foreground
        elif button_shape.id == self.game2_button.id:
            self.game2_button.update_rotate = True
            self.game2_button.sprite.image = resources.game2_button_img
            self.game2_button.sprite.group = self.foreground
        elif button_shape.id == self.game3_button.id:
            self.game3_button.update_rotate = True
            self.game3_button.sprite.image = resources.game3_button_img
            self.game3_button.sprite.group = self.foreground
        elif button_shape.id == self.game1_hs_button.id:
            self.game1_hs_button.update_rotate = True
            self.game1_hs_button.sprite.image = resources.game1_hs_button_img
            self.game1_hs_button.sprite.group = self.foreground
        elif button_shape.id == self.game2_hs_button.id:
            self.game2_hs_button.update_rotate = True
            self.game2_hs_button.sprite.image = resources.game2_hs_button_img
            self.game2_hs_button.sprite.group = self.foreground

    def on_mouse_press(self, x, y, button, modifier):
        point_q = self.space.point_query_nearest((x, y), 0, self.buttons)
        if point_q:
            if point_q.shape.body.id == self.game1_button.id:
                self.change_to = Game1.id
            elif point_q.shape.body.id == self.game2_button.id:
                self.change_to = Game2.id
            elif point_q.shape.body.id == self.game3_button.id:
                self.change_to = Game3.id
            elif point_q.shape.body.id == self.game1_hs_button.id:
                self.kwargs['game'] = Game1.name
                self.change_to = HighScore.id
            elif point_q.shape.body.id == self.game2_hs_button.id:
                self.kwargs['game'] = Game2.name
                self.change_to = HighScore.id
            elif point_q.shape.body.id == self.gravity_button.id:
                self.changing_gravity = not self.changing_gravity
            elif point_q.shape.body.id == self.fullscreen_button.id:
                self.window.set_fullscreen(not self.window.fullscreen)
                self.change_to = Menu.id
            if self.change_to:
                self.player.engine_sound.delete()

    def update(self):
        self.time += 1/60
        self.parallax.update(self.time*150)
        if self.changing_gravity:
            min_g, max_g= -900, 900
        else:
            min_g, max_g= -50, 50
        gravityx, gravityy = self.space.gravity
        if max_g < gravityx:
            self.adder[0] = -10
        elif gravityx < min_g:
            self.adder[0] = 10
        if max_g < gravityy:
            self.adder[1] = -15
        elif gravityy < min_g:
            self.adder[1] = 15
        self.space.gravity = gravityx+self.adder[0], gravityy+self.adder[1]

        self.player.update()
        self.terrain.update()
        self.obstacles.update()
        self.game1_button.update()
        self.game2_button.update()
        self.game3_button.update()
        self.game1_hs_button.update()
        self.game2_hs_button.update()
        self.gravity_button.update()
        self.fullscreen_button.update()
###############################################################################
class Game1(GameState):
    id = 4
    name = 'hillclimb'
    def __init__(self, batch, space, window):
        super().__init__(batch, space, window)
        self.event_handlers.append(self.on_mouse_press)
        self.ENDGAME = False
        self.time = 0
        self.end_position = 27000
        # objects #############################################################
        self.tank1 = Tank(self.batch, self.space, self.window,
            (window.width//2-120, 550), add_boxlives=True, group=self.background)
        self.event_handlers.extend(self.tank1.event_handlers)
        self.terrain = Terrain(self.batch, self.space, self.window,
            interval=50, mid_height=170, height_change=0.5,
            group=self.background)
        self.terrain.update(x_offset=self.window.width//2-520, update_all=True)
        self.obstacles = Obstacles(self.batch, self.space, self.window, amount=3, group=self.back)
        # left bound
        bounds_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        bounds_body.position = (0, 0)
        left_bound_s = pymunk.Segment(bounds_body, 
                                    (300-20, 0), (300-20, self.window.height), 20)
        left_bound_s.filter = pymunk.ShapeFilter(categories=0b0001000, mask=0b1110111)
        # buttons #############################################################
        self.menu_button = pyglet.sprite.Sprite(img=resources.menu_button_img,
            x=55, y=self.window.height-35, batch=self.batch, group=self.front)
        # labels ##############################################################
        self.score_label = pyglet.text.Label('',
                                            # font_name='Times New Roman',
                                            font_size=36,
                                            x=self.window.width-440, y=self.window.height-110,
                                            color=(0,0,0,255),
                                            anchor_x='right', anchor_y='baseline',
                                            batch=self.batch, group=self.front
                                            )
        # sprites #############################################################
        # finish flag sprite
        self.finishflag_sprite = pyglet.sprite.Sprite(img=resources.finishflag_img,
            x=self.end_position, y=self.window.height//2-100, batch=self.batch, group=self.back)
        # motor meter sprite
        self.motormeter_sprite = MeterSprite(self.batch, (self.window.width//2-320, 50), group=self.midground)
        # speed meter sprite
        self.speedmeter_sprite = MeterSprite(self.batch, (self.window.width//2+320, 50), group=self.midground)
        # goal sprite
        self.goalmeter_sprite = GoalSprite(self.batch, (self.window.width-230, self.window.height-80), group=self.background)
        #######################################################################
        self.space.add(bounds_body, left_bound_s)
        self.window.push_handlers(*self.event_handlers)
        # sound fx ############################################################
        self.tank1.engine_sound.volume = 1
        self.parallax = ParallaxBG(self.batch, self.window.get_size(), randrange(6))
    
    def on_mouse_press(self, x, y, button, modifier):
        if self.menu_button.x-self.menu_button.width//2 < x < self.menu_button.x+self.menu_button.width//2 and\
           self.menu_button.y-self.menu_button.height//2 < y < self.menu_button.y+self.menu_button.height//2:
            self.tank1.engine_sound.delete()
            self.change_to = Menu.id
        else:
            x += self.tank1.position[0]-400
            point_q = self.space.point_query_nearest((x, y), 0, self.buttons)
            if point_q:
                if point_q.shape.body.id == self.restart_button.id:
                    self.tank1.engine_sound.delete()
                    self.change_to = Game1.id

    def update(self):
        # update variables
        offset = self.tank1.position[0]-400
        self.time += 1/60
        score = 0 if self.ENDGAME else -self.time + self.tank1.lives*10 + 130
        self.score_label.text = '{:.1f} pts'.format(score)

        # if player is dead 
        if not self.ENDGAME and (self.tank1.lives == 0 or score < 0):
            self.tank1.torque = 0
            self.ENDGAME = True
            # create restart button ###########################################
            self.restart_button = Button(self.batch, self.space, 'restart_button', 
                (self.tank1.position[0], self.tank1.position[1]+130), resources.restart_button_img, 60)
            ###################################################################
        
        # if player won
        if self.tank1.position[0] > self.end_position:
            self.tank1.torque = 0
            self.kwargs['score'] = score
            self.kwargs['game'] = self.name
            self.tank1.engine_sound.delete()
            self.change_to = Endgame.id

        # update sprites 
        self.finishflag_sprite.update(x=self.end_position-offset)
        self.motormeter_sprite.update(abs(self.tank1.wheels[0].body.angular_velocity)/130)
        self.speedmeter_sprite.update(abs(self.tank1.chassis.body.velocity.x)/650)
        self.goalmeter_sprite.update(self.tank1.position[0]/self.end_position)
        self.parallax.update(offset=offset)
        # update objects
        if self.ENDGAME:
            self.restart_button.update(offset)
        self.tank1.update(offset)
        self.terrain.update(offset)
        self.obstacles.update(offset)
###############################################################################
class Game2(GameState):
    id = 5
    name = 'motor_race'
    def __init__(self, batch, space, window):
        super().__init__(batch, space, window)
        self.event_handlers.append(self.on_mouse_press)
        self.ENDGAME = False
        self.time = 0
        self.end_position = 27000
        # objects #############################################################
        self.motorbike = MotorBike(self.batch, self.space, self.window,
            (window.width//2-120, 550), group=self.background)
        self.event_handlers.extend(self.motorbike.event_handlers)
        self.terrain = Terrain(self.batch, self.space, self.window,
            interval=120, mid_height=170, height_change=0.3, color_set='gray',
            group=self.background)
        self.terrain.update(x_offset=self.window.width//2-520, update_all=True)
        self.obstacles = Obstacles(self.batch, self.space, self.window, 
            radius_range=(10, 20), frequency=150, amount=1, group=self.back)
        # left bound
        bounds_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        bounds_body.position = (0, 0)
        left_bound_s = pymunk.Segment(bounds_body, 
                                    (300-20, 0), (300-20, self.window.height), 20)
        left_bound_s.filter = pymunk.ShapeFilter(categories=0b0001000, mask=0b1110111)
        # buttons #############################################################
        self.menu_button = pyglet.sprite.Sprite(img=resources.menu_button_img,
            x=55, y=self.window.height-35, batch=self.batch, group=self.front)
        # labels ##############################################################
        self.time_label = pyglet.text.Label('',
                                            # font_name='Times New Roman',
                                            font_size=36,
                                            x=self.window.width-440, y=self.window.height-110,
                                            color=(0,0,0,255),
                                            anchor_x='right', anchor_y='baseline',
                                            batch=self.batch, group=self.front
                                            )
        # sprites #############################################################
        # finish flag sprite
        self.finishflag_sprite = pyglet.sprite.Sprite(img=resources.finishflag_img, 
            x=self.end_position, y=self.window.height//2-100, batch=self.batch, group=self.back)
        # motor meter sprite
        self.motormeter_sprite = MeterSprite(self.batch, (self.window.width//2-320, 50), group=self.midground)
        # speed meter sprite
        self.speedmeter_sprite = MeterSprite(self.batch, (self.window.width//2+320, 50), group=self.midground)
        # goal sprite
        self.goalmeter_sprite = GoalSprite(self.batch, (self.window.width-230, self.window.height-80), group=self.background)
        #######################################################################
        self.space.add(bounds_body, left_bound_s)
        self.window.push_handlers(*self.event_handlers)
        # sound fx ############################################################
        self.motorbike.engine_sound.volume = 0.8
        self.parallax = ParallaxBG(self.batch, self.window.get_size(), randrange(6))
    
    def on_mouse_press(self, x, y, button, modifier):
        if self.menu_button.x-self.menu_button.width//2 < x < self.menu_button.x+self.menu_button.width//2 and\
           self.menu_button.y-self.menu_button.height//2 < y < self.menu_button.y+self.menu_button.height//2:
            self.motorbike.engine_sound.delete()
            self.change_to = Menu.id

    def update(self):
        # update variables
        self.time += 1/60
        self.time_label.text = '{:.1f} s'.format(self.time)
        offset = self.motorbike.position[0]-400

        # if player won
        if self.motorbike.position[0] > self.end_position:
            self.motorbike.torque = 0
            self.kwargs['score'] = self.time
            self.kwargs['game'] = self.name
            self.motorbike.engine_sound.delete()
            self.change_to = Endgame.id

        # update sprites 
        self.finishflag_sprite.update(x=self.end_position-offset)
        self.motormeter_sprite.update(abs(self.motorbike.wheels[0].body.angular_velocity)/35)
        self.speedmeter_sprite.update(abs(self.motorbike.chassis.body.velocity.x)/1100)
        self.goalmeter_sprite.update(self.motorbike.position[0]/self.end_position)
        self.parallax.update(offset=offset)
        # update objects
        self.motorbike.update(offset)
        self.terrain.update(offset)
        self.obstacles.update(offset)
###############################################################################
class Game3(GameState):
    id = 6
    name = 'volleyball'
    def __init__(self, batch, space, window):
        super().__init__(batch, space, window)
        self.keys = pyglet.window.key.KeyStateHandler()
        self.event_handlers.extend((self.keys, self.on_mouse_press))

        self.ENDGAME = False
        self.time = 0
        # objects #############################################################
        ceiling = 1800
        bounds_shapes = []
        bounds_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        bounds_body.position = (0, 0)
        bounds_filter = pymunk.ShapeFilter(categories=0b0001000, mask=0b1110111)
        left_bound_s = pymunk.Segment(bounds_body, 
                                    (-20, 0), (-20, self.window.height+ceiling), 20)
        right_bound_s = pymunk.Segment(bounds_body, 
                                    (self.window.width+20, 0), 
                                    (self.window.width+20, self.window.height+ceiling), 20)
        upper_bound_s = pymunk.Segment(bounds_body, 
                                    (self.window.width, self.window.height+20+ceiling),
                                    (0, self.window.height+20+ceiling), 20)
        bounds_shapes.extend((left_bound_s, right_bound_s, upper_bound_s))
        for shape in bounds_shapes:
            shape.friction = 0.8
            shape.elasticity = 1
            shape.filter = bounds_filter
        ###################################################################
        self.space.add(bounds_body, *bounds_shapes)
        self.ball = None
        self.floor = SymmetricTerrain(self.batch, self.space, self.window,
            group=self.background)
        net_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        net_body.position = (self.window.width//2, 160)
        net_shape = pymunk.Segment(net_body, (0, -200), (0, 200), 6)
        net_shape.filter = pymunk.ShapeFilter(categories=0b0001000, mask=0b1110111)
        net_shape.elasticity = 0.5
        net_shape.friction = 0.9
        self.net_sprite = pyglet.sprite.Sprite(
            img=resources.vb_net_img,
            x=net_body.position.x, y=net_body.position.y, batch=self.batch, group=self.back)
        boundary_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        boundary_body.position = (self.window.width//2, 0)
        boundary_shape = pymunk.Segment(boundary_body, (0, 0), (0, ceiling), 6)
        boundary_shape.filter = pymunk.ShapeFilter(categories=0b0010000, mask=0b1110000)
        self.space.add(net_body, net_shape, boundary_body, boundary_shape)
        self.player1 = VbVehicle(self.batch, self.space, self.window,
            (window.width//4, 250), group=self.background)
        self.player2 = VbVehicle(self.batch, self.space, self.window,
            ((window.width//4)*3, 250), side='right', group=self.background)
        self.player1.score = 0
        self.player2.score = 0
        # buttons #############################################################
        self.menu_button = pyglet.sprite.Sprite(img=resources.menu_button_img,
            x=55, y=self.window.height-35, batch=self.batch, group=self.front)
        # labels ##############################################################
        self.dialog_label = pyglet.text.Label('',
                                            # font_name='Times New Roman',
                                            font_size=36,
                                            x=self.window.width/2, y=self.window.height-80,
                                            color=(0,0,0,255),
                                            anchor_x='center', anchor_y='bottom',
                                            batch=self.batch, group=self.front
                                            )
        self.p1score_label = pyglet.text.Label('2',
                                            # font_name='Times New Roman',
                                            font_size=56,
                                            x=self.window.width//2-50, y=40,
                                            color=(255,255,255,255),
                                            anchor_x='right', anchor_y='bottom',
                                            batch=self.batch, group=self.front
                                            )
        self.p2score_label = pyglet.text.Label('1',
                                            # font_name='Times New Roman',
                                            font_size=56,
                                            x=self.window.width//2+50, y=40,
                                            color=(255,255,255,255),
                                            anchor_x='left', anchor_y='bottom',
                                            batch=self.batch, group=self.front
                                            )
        # sprites #############################################################
        self.motormeter1_sprite = MeterSprite(self.batch, (110, 50), scale=0.8, group=self.midground)
        self.motormeter2_sprite = MeterSprite(self.batch, (self.window.width-110, 50), scale=0.8, group=self.midground)
        self.ball_indicator = BallIndicator(self.batch, self.window, self.front)
        # sound fx ############################################################
        self.player1.engine_sound.volume = 0.6
        self.player2.engine_sound.volume = 0.6
        self.parallax = ParallaxBG(self.batch, self.window.get_size(), randrange(6))
        #######################################################################
        self.space.add_collision_handler(self.COLLTYPE_VB_BALL, 
            self.COLLTYPE_VB_PLAYER1).begin = self.player2_scored
        self.space.add_collision_handler(self.COLLTYPE_VB_BALL, 
            self.COLLTYPE_VB_PLAYER2).begin = self.player1_scored
        self.window.push_handlers(*self.event_handlers)
        pyglet.clock.schedule_once(self.dialog, 0, message='Game Start!')
        pyglet.clock.schedule_once(self.dialog, 1, message='Dropping ball in:')
        pyglet.clock.schedule_once(self.dialog, 2, message=3)
        pyglet.clock.schedule_once(self.spawn_ball, 5, side=choice((1, 2)))
    
    def on_mouse_press(self, x, y, button, modifier):
        if self.menu_button.x-self.menu_button.width//2 < x < self.menu_button.x+self.menu_button.width//2 and\
           self.menu_button.y-self.menu_button.height//2 < y < self.menu_button.y+self.menu_button.height//2:
            self.player1.engine_sound.delete()
            self.player2.engine_sound.delete()
            self.change_to = Menu.id

    def player1_scored(self, arbiter, space, data):
        self.delete_ball()
        print('player1 scored')
        self.player1.score += 1
        if self.player1.score == 7:
            pyglet.clock.schedule_once(self.dialog, 0, message='Player 1 wins!')
        else:
            pyglet.clock.schedule_once(self.dialog, 0, message='Player 1 scored!')
            pyglet.clock.schedule_once(self.dialog, 1, message='Dropping ball for player 2')
            pyglet.clock.schedule_once(self.dialog, 2, message=2)
            pyglet.clock.schedule_once(self.spawn_ball, 4, side=1)
        return True

    def player2_scored(self, arbiter, space, data):
        self.delete_ball()
        print('player2 scored')
        self.player2.score += 1
        if self.player2.score == 7:
            pyglet.clock.schedule_once(self.dialog, 0, message='Player 2 wins!')
        else:
            pyglet.clock.schedule_once(self.dialog, 0, message='Player 2 scored!')
            pyglet.clock.schedule_once(self.dialog, 1, message='Dropping ball for player 1')
            pyglet.clock.schedule_once(self.dialog, 2, message=2)
            pyglet.clock.schedule_once(self.spawn_ball, 4, side=2)
        return True

    def dialog(self, dt, message, dismiss=False):
        if isinstance(message, int):
            pyglet.clock.schedule_once(self.countdown, 0, message)
        else:
            self.dialog_label.text = message
        if dismiss:
            pyglet.clock.schedule_once(self.dismiss_dialog, 3)

    def countdown(self, dt, x):
        if x == 0:
            self.dialog_label.text = ''
        else:
            self.dialog_label.text = str(x)
            pyglet.clock.schedule_once(self.countdown, 1, x-1)

    def dismiss_dialog(self, dt):
        self.dialog_label.text = ''

    def delete_ball(self):
        if self.ball:
            self.ball.delete()
        self.ball = None

    def spawn_ball(self, dt, side):
        offset = 0
        if side == 1:
            offset = 3
        elif side == 2:
            offset = 1
        self.ball = GameBall(self.batch, self.space, ((self.window.width//4)*offset, 700), 70, group=self.front)

    def update(self):
        # update variables
        self.time += 1/60

        # update labels
        # self.time_label.text = '{:.1f} s'.format(self.time)
        self.p1score_label.text = str(self.player1.score)
        self.p2score_label.text = str(self.player2.score)

        # update sprites 
        self.motormeter1_sprite.update(abs(min(self.player1.wheels[0].body.angular_velocity, self.player1.wheels[1].body.angular_velocity))/37)
        self.motormeter2_sprite.update(abs(min(self.player2.wheels[0].body.angular_velocity, self.player2.wheels[0].body.angular_velocity))/37)
        self.parallax.update(self.time*150)
        if self.ball:
            self.ball_indicator.update(self.ball.body.position.x, self.ball.body.position.y)

        # update objects
        if self.keys[pyglet.window.key.W]:
            self.player1.extend()
        elif self.keys[pyglet.window.key.S]:
            self.player1.jump()
        else:
            self.player1.rest()
        if self.keys[pyglet.window.key.A]:
            self.player1.reverse()
        if self.keys[pyglet.window.key.D]:
            self.player1.forward()
        if not (self.keys[pyglet.window.key.D] or self.keys[pyglet.window.key.A]):
            self.player1.stop()
        if self.keys[pyglet.window.key.UP]:
            self.player2.extend()
        elif self.keys[pyglet.window.key.DOWN]:
            self.player2.jump()
        else:
            self.player2.rest()
        if self.keys[pyglet.window.key.RIGHT]:
            self.player2.forward()
        if self.keys[pyglet.window.key.LEFT]:
            self.player2.reverse()
        if not (self.keys[pyglet.window.key.RIGHT] or self.keys[pyglet.window.key.LEFT]):
            self.player2.stop()

        if self.ball:
            self.ball.update()
        self.player1.update()
        self.player2.update()
###############################################################################
class HighScore(GameState):
    id = 3
    def __init__(self, batch, space, window, *args, **kwargs):
        super().__init__(batch, space, window, mouse_hover=True, bounded=True)
        self.score = kwargs.get('score')
        self.game = kwargs.get('game')
        self.choice = 0
        self.time = 0

        self.names_text = 'None'
        self.scores_text = 'None'
        # objects #############################################################
        if self.game == Game1.name:
            self.player = Tank(self.batch, self.space, self.window, 
                               (self.window.width//2, 600), group=self.background)
            color_set = 'green'
        elif self.game == Game2.name:
            self.player = MotorBike(self.batch, self.space, self.window, 
                               (self.window.width//2, 600), group=self.background)
            color_set = 'gray'
        self.terrain = Terrain(self.batch, self.space, self.window,
                                mid_height=400, end_coordinate=self.window.width+200, 
                                color_set=color_set,
                                group=self.background)
        self.obstacles = Obstacles(self.batch, self.space, self.window,
            end_coordinate=self.window.width, frequency=30,
            amount=1, x_offset=1600, min_height=450, group=self.background)
        # buttons #############################################################
        self.menu_button = pyglet.sprite.Sprite(img=resources.menu_button_img,
            x=55, y=self.window.height-35, batch=self.batch, group=self.front)
        # labels ##############################################################
        self.highscore_label = pyglet.text.Label(
                               'Highscores:',
                               # font_name='Times New Roman',
                               font_size=32,
                               x=647-330, y=420-70,
                               color=(255,255,255,255),
                               anchor_x='left', anchor_y='baseline',
                               batch=self.batch, group=self.foreground)
        # scrolling hs ########################################################
        self.score_scroll = ScrollingText(self.batch, (325, 100-70), 290-210,
            300, self.scores_text, align='right', group=self.foreground)
        self.name_scroll = ScrollingText(self.batch, (325+100, 100-70), 290+200,
            300, self.names_text, group=self.foreground)
        #######################################################################
        self.event_handlers.extend((
            self.on_mouse_press,
        ))

        self.window.push_handlers(*self.event_handlers)

        self.update_hs_text()
        # sound fx ############################################################
        self.player.engine_sound.volume = 0.6
        self.parallax = ParallaxBG(self.batch, self.window.get_size(), randrange(6))

    def update(self):
        self.time += 1/60
        self.parallax.update(self.time*150)
        self.choice = (self.choice + choice((-1, 1))) % 12
        if self.choice >= 6:
            self.player.forward()
        else:
            self.player.reverse()
        self.player.update()
        self.obstacles.update()
        self.score_scroll.update()
        self.name_scroll.update()

    def update_hs_text(self): # 38 chars
        self.scores_text = ''
        self.names_text = ''
        highscores = get_highscores('{}.csv'.format(self.game))
        if highscores:
            for hs_set in highscores:
                self.scores_text += '{:>5.1f}\n'.format(hs_set[1])
                self.names_text += '{:<32}\n'.format(hs_set[0])
            self.score_scroll.update_text(self.scores_text)
            self.name_scroll.update_text(self.names_text)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.menu_button.x-self.menu_button.width//2 < x < self.menu_button.x+self.menu_button.width//2 and\
           self.menu_button.y-self.menu_button.height//2 < y < self.menu_button.y+self.menu_button.height//2:
            self.player.engine_sound.delete()
            self.change_to = Menu.id
###############################################################################
class Endgame(GameState):
    id = 2
    def __init__(self, batch, space, window, *args, **kwargs):
        super().__init__(batch, space, window, mouse_hover=True, bounded=True)
        self.score = kwargs.get('score')
        self.game = kwargs.get('game')
        self.choice = 0
        self.time = 0

        if self.game == Game2.name:
            self.units = ' s'
        elif self.game  == Game1.name:
            self.units = ' pts'
        else:
            self.units = ''
        self.names_text = 'None'
        self.scores_text = 'None'
        # objects #############################################################
        if self.game == Game1.name:
            self.player = Tank(self.batch, self.space, self.window, 
                               (self.window.width//2, 600), group=self.background)
            color_set = 'green'
        elif self.game == Game2.name:
            self.player = MotorBike(self.batch, self.space, self.window, 
                               (self.window.width//2, 600), group=self.background)
            color_set = 'gray'
        self.terrain = Terrain(self.batch, self.space, self.window,
                                mid_height=400, end_coordinate=self.window.width+200, 
                                color_set=color_set, group=self.background)
        self.obstacles = Obstacles(self.batch, self.space, self.window,
            end_coordinate=self.window.width, frequency=30,
            amount=1, x_offset=1600, min_height=450, group=self.background)
        # buttons #############################################################
        self.enter_button = Button(self.batch, self.space, 'enter_button', (640-80, 120),
            resources.enter_button_img, (120, 50), pymunk.Body.STATIC, sensor=True
        )
        self.menu_button = pyglet.sprite.Sprite(img=resources.menu_button_img,
            x=55, y=self.window.height-35, batch=self.batch, group=self.front)
        # labels ##############################################################
        self.name_label = pyglet.text.Label(
                          'Enter your name:',
                          # font_name='Times New Roman',
                          font_size=36,
                          x=21, y=180,
                          color=(255,255,255,255),
                          anchor_x='left', anchor_y='center',
                          batch=self.batch, group=self.foreground
                          )
        self.highscore_label = pyglet.text.Label(
                               'Highscores:',
                               # font_name='Times New Roman',
                               font_size=32,
                               x=647, y=420,
                               color=(255,255,255,255),
                               anchor_x='left', anchor_y='baseline',
                               batch=self.batch, group=self.foreground
                               )
        self.score = round(self.score, 1) if isinstance(self.score, float)\
                     else self.score
        self.score_label = pyglet.text.Label(
                           str(self.score)+self.units,
                           # font_name='Times New Roman',
                           font_size=115,
                           x=14, y=230,
                           color=(255,255,255,255),
                           anchor_x='left', anchor_y='baseline',
                           batch=self.batch, group=self.foreground
                           )
        # scrolling hs ########################################################
        self.score_scroll = ScrollingText(self.batch, (655, 100), 290-210,
            300, self.scores_text, align='right', group=self.foreground)
        self.name_scroll = ScrollingText(self.batch, (655+100, 100), 290+200,
            300, self.names_text, group=self.foreground)
        # userinput ###########################################################
        self.userinput = TextInput(self.batch, (30, 100), 440, 26, 
                                   group=self.foreground)
        #######################################################################
        self.event_handlers.extend((
            self.on_mouse_motion,
            self.on_mouse_press,
            self.on_mouse_drag,
            self.on_text,
            self.on_text_motion,
            self.on_text_motion_select,
            self.on_key_press
        ))

        self.window.push_handlers(*self.event_handlers)

        self.update_hs_text()
        # sound fx ############################################################
        self.player.engine_sound.volume = 0.6
        self.parallax = ParallaxBG(self.batch, self.window.get_size(), randrange(6))

    def update(self):
        self.time += 1/60
        self.parallax.update(self.time*150)
        self.choice = (self.choice + choice((-1, 1))) % 12
        if self.choice >= 6:
            self.player.forward()
        else:
            self.player.reverse()
        self.player.update()
        self.obstacles.update()
        self.enter_button.update()
        self.score_scroll.update()
        self.name_scroll.update()

    def update_hs_text(self): # 38 chars
        self.scores_text = ''
        self.names_text = ''
        highscores = get_highscores('{}.csv'.format(self.game))
        if highscores:
            for hs_set in highscores:
                self.scores_text += '{:>5.1f}\n'.format(hs_set[1])
                self.names_text += '{:<32}\n'.format(hs_set[0])
            self.score_scroll.update_text(self.scores_text)
            self.name_scroll.update_text(self.names_text)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.menu_button.x-self.menu_button.width//2 < x < self.menu_button.x+self.menu_button.width//2 and\
           self.menu_button.y-self.menu_button.height//2 < y < self.menu_button.y+self.menu_button.height//2:
            if self.userinput:
                self.__name_entered()
            self.player.engine_sound.delete()
            self.change_to = Menu.id
        elif self.userinput:
            self.userinput.caret.on_mouse_press(x, y, button, modifiers)

            point_q = self.space.point_query((x, y), 0, self.buttons)
            print(point_q)
            if point_q:
                if point_q[0].shape.body.id == self.enter_button.id:
                    self.__name_entered()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.userinput.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_text(self, text):
        if text not in whitespace and text != ',':
            self.userinput.caret.on_text(text)

    def on_text_motion(self, motion):
        self.userinput.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        self.userinput.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        if self.userinput and symbol == key.ENTER:
            self.__name_entered()

    def on_mouse_hover(self, arbiter, space, data):
        button_shape, mouse_shape = arbiter.shapes
        if button_shape.id == self.enter_button.id:
            self.enter_button.sprite.image = resources.enter_button_hover_img
        return True

    def on_mouse_unhover(self, arbiter, space, data):
        button_shape, mouse_shape = arbiter.shapes
        if button_shape.id == self.enter_button.id:
            self.enter_button.sprite.image = resources.enter_button_img

    def __name_entered(self):
        if self.game == Game1.name:
            ascending = False
        if self.game == Game2.name:
            ascending = True
        add_highscore(
            '{}.csv'.format(self.game), 
            self.userinput.document.text,
            self.score,
            ascending=ascending
        )
        del self.userinput
        self.userinput = None
        self.window.pop_handlers()
        self.window.push_handlers(
            self.on_mouse_press,
            self.on_key_press,
            self.on_mouse_motion
        )
        self.update_hs_text()

###############################################################################
if __name__ == "__main__":
    window = Window(1280, 720, 'Version 8', resizeable=False)
    pyglet.app.run()
