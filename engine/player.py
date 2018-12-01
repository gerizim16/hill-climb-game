from math import pi

import pyglet
from pyglet.window import key
import pymunk

from . import resources
from .physical_object import PhysicalObject
from .sound_loop import SoundLoop

def mapFromTo(x, a, b, c, d):
    y=(x-a)/(b-a)*(d-c)+c
    return y

class Vehicle(object):
    def __init__(self, batch, space, window, position, side='left', 
                 torque=1000, speed=2*pi):
        self.COLLTYPE_DEFAULT = 0
        self.COLLTYPE_BOXLIFE = 1
        self.COLLTYPE_SENSOR = 2

        self.batch = batch
        self.space = space
        self.window = window
        self.position = position # (x, y)
        self.side = 1 if side == 'left' else -1
        self.torque = torque
        self.speed = speed
        self.engine_sound = None
        self.min_pitch = 1
        self.max_pitch = 1

        self.chassis = None
        self.wheels = []
        self.motors = []
        self.constraints = []

        self.bodies = []
        self.shapes = []

        self.sprites = []

        self.physical_objects = []
        self.event_handlers = [self.on_key_press, self.on_key_release]

    def get_physical_object(self):
        return self.bodies + self.shapes + self.constraints

    def update(self, x_offset=0):
        self.position = self.chassis.body.position
        for physical_object in self.physical_objects:
            physical_object.update(x_offset)
        if self.engine_sound:
            self.engine_sound.pitch = mapFromTo(
                abs(self.wheels[0].body.angular_velocity),
                0, (self.speed+4), self.min_pitch, self.max_pitch
            )

    def forward(self):
        for motor in self.motors:
            motor.max_force = self.torque
            motor.rate = self.speed

    def reverse(self):
        for motor in self.motors:
            motor.max_force = self.torque
            motor.rate = -self.speed

    def stop(self):
        for motor in self.motors:
            motor.max_force = 0

    def on_key_release(self, symbol, modifiers):
        if symbol in (key.D, key.A):
            self.stop()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.D:
            self.forward()
        if symbol == key.A:
            self.reverse()

class Tank(Vehicle):
    name = 'tank'
    def __init__(self, batch, space, window, position, side='left', 
                 add_boxlives=False, torque=300000, speed=40*pi, group=None):
        super().__init__(batch, space, window, position, side=side,
                         torque=torque, speed=speed)
        self.add_boxlives = add_boxlives

        self.head = None
        self.threads = []
        self.boxlives = []

        self.__build_tank()
        for sprite in self.sprites:
            sprite.group = group

        self.lives = len(self.boxlives)
        self.space.add_collision_handler(self.COLLTYPE_BOXLIFE, 
            self.COLLTYPE_SENSOR).separate = self.boxlife_coll_sep

        self.space.add(self.get_physical_object())

        self.min_pitch, self.max_pitch = 0.2, 1.2
        self.engine_sound = SoundLoop(resources.engine_sfx)
        self.engine_sound.play()

    def boxlife_coll_sep(self, arbiter, space, data):
        boxlife_shape, sensor_shape = arbiter.shapes # box, sensor
        boxlife_shape.collision_type = self.COLLTYPE_DEFAULT
        boxlife_shape.filter = pymunk.ShapeFilter(categories=0b0000010, mask=0b1111111)
        self.boxlives[boxlife_shape.id].sprite.image = resources.boxlife_dead_img
        self.lives -= 1
        if self.lives == 0:
            self.torque = 0
        # print(boxlife_shape.id) # debug
        print(self.lives) # debug

    def __build_tank(self):
        self.__build_tank_body()
        self.__build_tank_wheels()
        self.__build_tank_threads()
        if self.add_boxlives:
            self.__build_boxlives()

    def __build_boxlives(self):
        x_offset = -140 if self.side == 1 else -120
        size = (50, 50)
        mass = 0.2
        boxlife_moment = pymunk.moment_for_box(mass, size)
        for i in range(5):
            position = (self.position[0]+x_offset+i*51, self.position[1]+65)
            boxlife_body = pymunk.Body(mass, boxlife_moment)
            boxlife_body.position = position
            boxlife_shape = pymunk.Poly.create_box(boxlife_body, size)
            boxlife_shape.filter = pymunk.ShapeFilter(categories=0b0000010, mask=0b1101111)
            boxlife_shape.elasticity = 0.7
            boxlife_shape.friction = 0.7
            boxlife_shape.collision_type = self.COLLTYPE_BOXLIFE
            boxlife_shape.id = i
            boxlife_sprite = pyglet.sprite.Sprite(
                img=resources.boxlife_img,
                x=boxlife_body.position.x, y=boxlife_body.position.y, batch=self.batch)
            boxlife = PhysicalObject(boxlife_body, boxlife_sprite)
            self.sprites.append(boxlife_sprite)
            self.bodies.append(boxlife_body)
            self.shapes.append(boxlife_shape)
            self.physical_objects.append(boxlife)
            self.boxlives.append(boxlife)

    def __build_tank_body(self):
        chassis_mass = 2.5
        chassis_coords = ((-125, -30), (125, -30), (175, 20), (165, 30),
                          (-175, 30), (-165, 0))
        # head_coords = ((-145, 40), (-145, 90), (-60, 110), (125, 90), (125, 40))
        head_coords = ((-145, 40), (-145, 300), (125, 300), (125, 40))
        bound1_coords = ((-145+2, 40), (-145+2, 90))
        bound2_coords = ((125-2, 40), (125-2, 90))
        bound3_coords = ((-145, 40-2), (125, 40-2))
        if self.side == -1:
            chassis_coords = tuple(map(lambda coord: (-coord[0], coord[1]), chassis_coords))
            head_coords = tuple(map(lambda coord: (-coord[0], coord[1]), head_coords))
            bound1_coords = tuple(map(lambda coord: (-coord[0], coord[1]), bound1_coords))
            bound2_coords = tuple(map(lambda coord: (-coord[0], coord[1]), bound2_coords))

        chassis_moment = pymunk.moment_for_poly(chassis_mass, chassis_coords)
        tank_body = pymunk.Body(chassis_mass, chassis_moment)
        tank_body.position = self.position[0], self.position[1]+10

        chassis_shape = pymunk.Poly(tank_body, chassis_coords)
        chassis_shape.filter = pymunk.ShapeFilter(categories=0b1000000, mask=0b1001111)
        chassis_shape.elasticity = 0.3
        chassis_shape.friction = 0.3

        head_shape = pymunk.Poly(tank_body, head_coords)
        head_shape.filter = pymunk.ShapeFilter(categories=0b1000000)
        head_shape.sensor = True
        head_shape.collision_type = self.COLLTYPE_SENSOR

        bound1_shape = pymunk.Segment(tank_body, bound1_coords[0], bound1_coords[1], 2)
        bound2_shape = pymunk.Segment(tank_body, bound2_coords[0], bound2_coords[1], 2)
        bound3_shape = pymunk.Segment(tank_body, bound3_coords[0], bound3_coords[1], 2)
        
        bound_shapes = [bound1_shape, bound2_shape, bound3_shape]

        for bound in bound_shapes:
            bound.filter = pymunk.ShapeFilter(categories=0b1000000, mask=0b0001111)
            bound.elasticity = 0.7
            bound.friction = 0.7

        chassis_sprite = pyglet.sprite.Sprite(
            img=resources.tank_body_img, 
            x=tank_body.position.x, y=tank_body.position.y, batch=self.batch)

        head_sprite = pyglet.sprite.Sprite(
            img=resources.tank_head_img, 
            x=tank_body.position.x, y=tank_body.position.y, batch=self.batch)
        if self.add_boxlives:
            head_sprite.opacity = 128

        if self.side == -1:
            chassis_sprite.scale_x = -1
            head_sprite.scale_x = -1

        chassis = PhysicalObject(tank_body, chassis_sprite)
        head = PhysicalObject(tank_body, head_sprite)

        self.sprites.extend((chassis_sprite, head_sprite))
        self.chassis = chassis
        self.bodies.append(tank_body)
        self.shapes.extend((chassis_shape, head_shape, *bound_shapes))
        self.physical_objects.extend((chassis, head))

    def __build_tank_wheels(self):
        mass = 0.75
        radius = 30
        x_offset = -140
        wheel_moment = pymunk.moment_for_circle(mass, 0, radius)
        gap = 70
        for i in range(5):
            wheel_body = pymunk.Body(mass, wheel_moment)
            wheel_body.position = (self.position[0] + x_offset) + gap*i,\
                self.position[1] if i in (0, 4) else self.position[1] - 60
            wheel_shape = pymunk.Circle(wheel_body, radius)
            wheel_shape.filter = pymunk.ShapeFilter(categories=0b0100000, mask=0b0111111)
            wheel_shape.elasticity = 0.3
            wheel_shape.friction = 0.95

            if i not in (0, 4):
                wheel_gj = pymunk.GrooveJoint(self.chassis.body, wheel_body, (wheel_body.position.x-self.chassis.body.position.x, 30), (wheel_body.position.x-self.chassis.body.position.x, -60), (0, 0))
                wheel_ds = pymunk.DampedSpring(self.chassis.body, wheel_body, (wheel_body.position.x-self.chassis.body.position.x, 30), (0, 0), 95, 250, 20)
                self.constraints.append(wheel_gj)
                self.constraints.append(wheel_ds)
            else:
                wheel_pj = pymunk.PivotJoint(self.chassis.body, wheel_body, wheel_body.position)
                self.constraints.append(wheel_pj)
                wheel_m = pymunk.SimpleMotor(self.chassis.body, wheel_body, 3*pi)
                wheel_m.max_force = 0
                self.constraints.append(wheel_m)
                self.motors.append(wheel_m)

            wheel_sprite = pyglet.sprite.Sprite(
                img=resources.wheel_img, 
                x=wheel_body.position.x, y=wheel_body.position.y, batch=self.batch)
            wheel = PhysicalObject(wheel_body, wheel_sprite)
            self.sprites.append(wheel_sprite)
            self.wheels.append(wheel)
            self.bodies.append(wheel_body)
            self.shapes.append(wheel_shape)
            self.physical_objects.append(wheel)

    def __build_tank_threads(self):
        mass = 0.25
        length = 24 # 24
        thickness = 3 # 3
        x_amount = 12 # 12
        y_amount = 4 # 4
        x_offset = self.position[0] - 145
        y_offset = self.position[1] + 10
        thread_moment = pymunk.moment_for_box(mass, (length, thickness))
        end_coords = [] # endpoints position on world coords
        pos_coords = []
        for i in range(x_amount):
            end_coord = (x_offset+length*i, y_offset)
            end_coords.append(end_coord)
            pos_coord = (end_coord[0]+length/2, end_coord[1])
            pos_coords.append(pos_coord)
        for i in range(y_amount):
            end_coord = (x_offset+length*x_amount, y_offset-length*i)
            end_coords.append(end_coord)
            pos_coord = (end_coord[0], end_coord[1]-length/2)
            pos_coords.append(pos_coord)
        for i in range(x_amount):
            end_coord = (x_offset+length*(x_amount-i), y_offset-length*y_amount)
            end_coords.append(end_coord)
            pos_coord = (end_coord[0]-length/2, end_coord[1])
            pos_coords.append(pos_coord)
        for i in range(y_amount):
            end_coord = (x_offset, y_offset-length*(y_amount-i))
            end_coords.append(end_coord)
            pos_coord = (end_coord[0], end_coord[1]+length/2)
            pos_coords.append(pos_coord)
        for i, pos_coord in enumerate(pos_coords):
            dimensions = ((-length/2, 0), (length/2, 0))     \
                if 0 <= i < x_amount or                      \
                x_amount+y_amount <= i < 2*x_amount+y_amount \
                else ((0, -length/2), (0, length/2))
            thread_body = pymunk.Body(mass, thread_moment)
            thread_body.position = pos_coord
            thread_shape = pymunk.Segment(thread_body, dimensions[0], dimensions[1], thickness)
            thread_shape.filter = pymunk.ShapeFilter(categories=0b0010000, mask=0b0101111)
            thread_shape.elasticity = 0.3
            thread_shape.friction = 0.95
            thread_sprite = pyglet.sprite.Sprite(
                img=resources.thread_img, 
                x=thread_body.position.x, y=thread_body.position.y, batch=self.batch)
            rotation_offset = 0 if 0 <= i < x_amount or      \
                x_amount+y_amount <= i < 2*x_amount+y_amount \
                else 90
            thread = PhysicalObject(thread_body, thread_sprite, rotation_offset)
            self.sprites.append(thread_sprite)
            self.threads.append(thread)
            self.bodies.append(thread_body)
            self.shapes.append(thread_shape)
            self.physical_objects.append(thread)
        for i, joint_coord in enumerate(end_coords, -1):
            i = i % (2*(x_amount+y_amount))
            j = (i + 1) % (2*(x_amount+y_amount))
            thread_joint = pymunk.PivotJoint(self.threads[i].body, self.threads[j].body, joint_coord)
            self.constraints.append(thread_joint)

class MotorBike(Vehicle):
    name = 'motorbike'
    def __init__(self, batch, space, window, position, side='left', 
                 torque=120000, speed=11*pi, group=None):
        super().__init__(batch, space, window, position, side=side,
                         torque=torque, speed=speed)

        self.__build_motorbike()
        for sprite in self.sprites:
            sprite.group = group

        self.event_handlers = (self.on_key_press, self.on_key_release)
        self.space.add(self.get_physical_object())

        self.min_pitch, self.max_pitch = 1, 3
        self.engine_sound = SoundLoop(resources.engine_sfx)
        self.engine_sound.play()

    def on_key_release(self, symbol, modifiers):
        if symbol in (key.D, key.A):
            self.rotator.max_force = 0
            self.motors[0].max_force = 10000
            self.motors[0].rate = 0

    def on_key_press(self, symbol, modifiers):
        if symbol == key.D:
            self.rotator.max_force = 170000
            self.rotator.rate = 6*pi
            self.motors[0].max_force = self.torque
            self.motors[0].rate = self.speed
        if symbol == key.A:
            self.rotator.max_force = 300000
            self.rotator.rate = -6*pi
            self.motors[0].max_force = 50000
            self.motors[0].rate = 0

    def __build_motorbike(self):
        self.__build_chassis()
        self.__build_wheels()

    def __build_chassis(self):
        chassis_mass = 1.25
        chassis_coords = (
            ((-170, 40), (-140, 30), (-105, 25), (-105, 40)),
            ((-105, 40), (-105, 25), (-55, -10), (-30, 35)),
            ((-30, 35), (-55, -10), (-35, -50), (20, -45), (50, 40), (35, 70)),
            # ((30, 90), (20, 85), (75, -15), (85, -5)),
            ((50, 50), (40, 20), (80, 40), (85, 50)),
            ((85, 50), (80, 40), (135, 25), (115, 40)),
        )
        chassis_moment = 0
        for coord in chassis_coords:
            chassis_moment += pymunk.moment_for_poly(chassis_mass, coord)
        chassis_body = pymunk.Body(chassis_mass, chassis_moment)
        chassis_body.position = self.position

        chassis_shapes = []
        for coord in chassis_coords:
            chassis_shape = pymunk.Poly(chassis_body, coord)
            chassis_shape.filter = pymunk.ShapeFilter(categories=0b1000000, mask=0b1111111)
            chassis_shape.elasticity = 0.5
            chassis_shape.friction = 0.7
            chassis_shapes.append(chassis_shape)

        chassis_sprite = pyglet.sprite.Sprite(
            img=resources.motorbike_chassis_img, 
            x=chassis_body.position.x, y=chassis_body.position.y, 
            batch=self.batch)

        chassis = PhysicalObject(chassis_body, chassis_sprite)

        self.sprites.append(chassis_sprite)
        self.chassis = chassis
        self.bodies.append(chassis_body)
        self.shapes.extend(chassis_shapes)
        self.physical_objects.append(chassis)

        body_rotator = pymunk.Body(body_type=pymunk.Body.STATIC)
        body_rotator.position = 0, 0
        chassis_rotator = pymunk.SimpleMotor(self.chassis.body, body_rotator, 5*pi)
        chassis_rotator.max_force = 0
        self.constraints.append(chassis_rotator)
        self.rotator = chassis_rotator

    def __build_wheels(self):
        x, y = self.position
        mass = 0.5
        radius = 50
        moment = pymunk.moment_for_circle(mass, 0, radius)
        wheel_filter = pymunk.ShapeFilter(categories=0b0100000, mask=0b1111111)

        wheel1_body = pymunk.Body(mass, moment)
        wheel1_body.position = x-120, y-50
        wheel1_shape = pymunk.Circle(wheel1_body, radius)
        wheel1_shape.elasticity = 0.3
        wheel1_shape.friction = 0.95
        wheel1_shape.filter = wheel_filter
        wheel1_sprite = pyglet.sprite.Sprite(
            img=resources.mb_wheel_img, 
            x=wheel1_body.position.x, y=wheel1_body.position.y, batch=self.batch)
        wheel1 = PhysicalObject(wheel1_body, wheel1_sprite)
        self.sprites.append(wheel1_sprite)
        self.wheels.append(wheel1)
        self.bodies.append(wheel1_body)
        self.shapes.append(wheel1_shape)
        self.physical_objects.append(wheel1)

        holder_mass = 1
        holder_radius = 5
        holder_pos1 = (45, 7.5)
        holder_pos2 = (-45, -7.5)
        holder_moment = pymunk.moment_for_segment(holder_mass, holder_pos1, holder_pos2, holder_radius)
        holder_body = pymunk.Body(holder_mass, holder_moment)
        holder_body.position = x-75, y-42.5
        holder_shape = pymunk.Segment(holder_body, holder_pos1, holder_pos2, holder_radius)
        holder_shape.elasticity = 0.2
        holder_shape.friction = 0.3
        holder_shape.filter = pymunk.ShapeFilter(categories=0b1000000, mask=0b0011111)
        holder_sprite = pyglet.sprite.Sprite(
            img=resources.mb_holder_img, 
            x=holder_body.position.x, y=holder_body.position.y, batch=self.batch)
        holder = PhysicalObject(holder_body, holder_sprite, -9.46)
        self.sprites.append(holder_sprite)
        self.bodies.append(holder_body)
        self.shapes.append(holder_shape)
        self.physical_objects.append(holder)

        wheel1_pj1 = pymunk.PivotJoint(holder_body, wheel1_body, wheel1_body.position)
        self.constraints.append(wheel1_pj1)
        wheel1_pj2 = pymunk.PivotJoint(holder_body, self.chassis.body,
            (holder_body.position.x+45, holder_body.position.y+7.5))
        self.constraints.append(wheel1_pj2)
        wheel1_ds = pymunk.DampedSpring(holder_body, self.chassis.body, holder_pos2, (-105, 40), 110, 70, 7)
        self.constraints.append(wheel1_ds)
        wheel1_m = pymunk.SimpleMotor(self.chassis.body, wheel1_body, 3*pi)
        wheel1_m.max_force = 0
        self.constraints.append(wheel1_m)
        self.motors.append(wheel1_m)

        wheel2_body = pymunk.Body(mass, moment)
        wheel2_body.position = x+110, y-50
        wheel2_shape = pymunk.Circle(wheel2_body, radius)
        wheel2_shape.elasticity = 0.5
        wheel2_shape.friction = 0.8
        wheel2_shape.filter = wheel_filter
        wheel2_sprite = pyglet.sprite.Sprite(
            img=resources.mb_wheel_img, 
            x=wheel2_body.position.x, y=wheel2_body.position.y, batch=self.batch)
        wheel2 = PhysicalObject(wheel2_body, wheel2_sprite)
        self.sprites.append(wheel2_sprite)
        self.wheels.append(wheel2)
        self.bodies.append(wheel2_body)
        self.shapes.append(wheel2_shape)
        self.physical_objects.append(wheel2)

        wheel2_gj = pymunk.GrooveJoint(self.chassis.body, wheel2_body, 
            (70, 0), (105, -55), (0, 0))
        self.constraints.append(wheel2_gj)
        wheel2_ds = pymunk.DampedSpring(wheel2_body, self.chassis.body, (0, 0), (50, 35), 110, 60, 7)
        self.constraints.append(wheel2_ds)
