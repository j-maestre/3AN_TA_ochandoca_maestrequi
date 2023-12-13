from PackageSetup import *

InstallPackage('pygame', True, False)

# Import necessary modules and libraries
import math
import sys
from random import randint, random
from typing import Union
import dearpygui.dearpygui as dpg
import threading
import queue
from functools import partial

import pygame
from openal import *
from Audio.AudioPlayer import *
from Audio.Branching import *

# Definition of a Point class using pygame.Vector2
Point = pygame.Vector2
fondo = None
gaviota = None
b = Branching()

# Initial runtime configurations
SMOOTH = True  # uses numpy + scipy
TEXTURE = True  # uses texture images
VOLUME_RISE = True
USE_PYMUNK = True  # uses pymunk
FPS = 60
GRAVITY = (0, 500)
DISPLAY_HELP = True

if SMOOTH:
    import numpy
    from scipy.interpolate import interp1d
if USE_PYMUNK:
    import pymunk

# Initialization of pygame
pygame.init()

# Pygame window setup
screen_width = 1200
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Water')
clock = pygame.time.Clock()

# Setup images and font for visual representation
font = pygame.font.SysFont('consolas', 25)
if TEXTURE:
    ROCK_IMAGE = pygame.image.load('empty.png').convert_alpha()
    BALL_IMAGE = pygame.image.load('ship.png').convert_alpha()

# Pymunk setup if used
if USE_PYMUNK:
    space = pymunk.Space()
    space.gravity = GRAVITY

def map_to_range(value, from_x, from_y, to_x, to_y):
    """
    Function to map a value from one range to another
    """
    return value * (to_y - to_x) / (from_y - from_x)

def create_rock(_space, x=None, y=None):
    """
    Function to create a rock in pymunk space
    """
    if x is None:
        x = screen_width // 2 + random()
    if y is None:
        y = 0
    mass = 3
    body = pymunk.Body(mass=mass * 5, moment=mass * 1, body_type=pymunk.Body.DYNAMIC)
    body.position = (x + random(), y)
    body.splashed = False
    shape = pymunk.Circle(body, body.mass * 1)
    if TEXTURE:
        shape.img = ROCK_IMAGE
        shape.img = pygame.transform.scale(shape.img, (shape.radius * 2, shape.radius * 2))
    shape.friction = 0.05
    _space.add(body, shape)
    return shape


def draw_rock(rock, surf: pygame.Surface):
    """
    Function to draw a rock on the pygame surface
    """
    if TEXTURE:
        try:
            angle = round(math.degrees(rock.body.angle))
        except ValueError:
            angle = 0
        img = pygame.transform.rotate(rock.img, -angle)
        surf.blit(img, img.get_rect(center=rock.body.position))
    else:
        pygame.draw.circle(surf, 'brown', rock.body.position, rock.radius)

def display_help():
    """
    Function to display game instructions on the screen
    """
    _text = [
        'Instructions set',
        '',
        'Q - Spawn gaviota',
        'W - Start raining',
        '',
        '-- Cross Fade --',
        'E - Start storm',
        'A - Awake tripulation',
        'S - Sleep tripulation',
        '',
        '-- Branching --',
        'Space - Change mode',
    ]
    y = 0
    for i in _text:
        y += 20
        text = font.render(i, True, 'white')
        screen.blit(text, (25, y))


class Ball:
    """
    Definition of the Ball class to represent a ball in the game
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.height = 42
        self.width = 20
        self.dy = 0
        self.spring: Union['WaterSpring', None] = None
        self.next_spring: Union['WaterSpring', None] = None
        self.rot = randint(0, 360)
        self.rot = 0
        self.gravity = 0.5
        self.water_force = 2
        self.on_water_surface = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= 1.0
        if keys[pygame.K_RIGHT]:
          self.x += 1.0
        if self.spring:
            if self.on_water_surface:
                self.y = self.spring.height - self.height
            else:
                self.dy -= self.water_force
                self.y += self.dy
                if self.dy < 0 and self.y < self.spring.height:
                    self.on_water_surface = True
        else:
            self.dy += self.gravity
            self.y += self.dy

    def draw(self, surf: pygame.Surface):
        size = 100
        if TEXTURE:
            img = pygame.transform.scale(BALL_IMAGE, (size, size))
            surf.blit(img, img.get_rect(center=(self.x, self.y)))
        else:
            pygame.draw.circle(surf, 'green', (self.x, self.y), size / 2)


class WaterSpring:
    """
    Definition of the WaterSpring class to represent a water spring
    """
    def __init__(self, x=0, target_height=None):
        if not target_height:
            self.target_height = screen_height // 2 + 150
        else:
            self.target_height = target_height
        self.dampening = 0.05  # adjust accordingly
        self.tension = 0.01
        self.height = self.target_height
        self.vel = 0
        self.x = x

    def update(self):
        dh = self.target_height - self.height
        if abs(dh) < 0.01:
            self.height = self.target_height
        self.vel += self.tension * dh - self.vel * self.dampening
        self.height += self.vel

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, 'white', (self.x, self.height), 1)


class Wave:
    """
    Definition of the Wave class to group water springs and simulate a wave
    """
    def __init__(self):
        diff = 20
        self.springs = [WaterSpring(x=i * diff + 0) for i in range(screen_width // diff + 2)]
        self.points = []
        self.diff = diff

    def get_spring_index_for_x_pos(self, x):
        return int(x // self.diff)

    def get_target_height(self):
        return self.springs[0].target_height

    def set_target_height(self, height):
        for i in self.springs:
            i.target_height = height

    def add_volume(self, volume):
        height = volume / screen_width
        self.set_target_height(self.get_target_height() - height)

    def update(self):
        for i in self.springs:
            i.update()
        self.spread_wave()
        self.points = [Point(i.x, i.height) for i in self.springs]
        if SMOOTH:
            self.points = get_curve(self.points)
        self.points.extend([Point(screen_width, screen_height), Point(0, screen_height)])

    def draw(self, surf: pygame.Surface):
        pygame.draw.polygon(surf, (0, 0, 255, 50), self.points)

    def draw_line(self, surf: pygame.Surface):
        pygame.draw.lines(surf, 'white', False, self.points[:-2], 5)

    def spread_wave(self):
        spread = 0.1
        for i in range(len(self.springs)):
            if i > 0:
                self.springs[i - 1].vel += spread * (self.springs[i].height - self.springs[i - 1].height)
            try:
                self.springs[i + 1].vel += spread * (self.springs[i].height - self.springs[i + 1].height)
            except IndexError:
                pass

    def splash(self, index, vel):
        try:
            self.springs[index].vel += vel
        except IndexError:
            pass


def get_curve(points):
    """
    Function to get a cubic interpolation of points for smoothing curves
    """
    x_new = numpy.arange(points[0].x, points[-1].x, 1)
    x = numpy.array([i.x for i in points[:-1]])
    y = numpy.array([i.y for i in points[:-1]])
    f = interp1d(x, y, kind='cubic', fill_value='extrapolate')
    y_new = f(x_new)
    x1 = list(x_new)
    y1 = list(y_new)
    points = [Point(x1[i], y1[i]) for i in range(len(x1))]
    return points

def lerp(a, b, t):
    """
    Function to perform linear interpolation
    """
    return a + t * (b - a)

def cross_fade(first_audio, second_audio, target_gain, dt):
    """
    Function to perform crossfade between two audio tracks
    """
    value1 = -1.0
    value2 = -1.0
   
    value1 = first_audio.get_gain()
    tmp = lerp(value1, 0.0, (0.5 * dt))
    # Solo cambiamos si es menor porque tiene que ir a 0
    if tmp < value1: 
        first_audio.set_gain(tmp)
    #print("First gain " + str(value1))

    
    value2 = second_audio.get_gain()
    tmp = lerp(value2, target_gain, (0.5 * dt))
    # Solo cambiamos si es mayor porque tiene que aumentar hasta el target
    if tmp > value2:
        second_audio.set_gain(tmp)
    print("First gain " + str(value1) + " Second gain " + str(value2))

    if(first_audio.get_gain() <= 0.05 and (second_audio.get_gain() + 0.05) >= target_gain):
        first_audio.is_cross_fading = False
        second_audio.is_cross_fading = False
        first_audio.set_gain(0.0)
        second_audio.set_gain(target_gain)
        return False
    else:
        return True



def create_walls():
    """
    Function to create static walls in pymunk
    """
    base = pymunk.Body(mass=10 ** 5, moment=0, body_type=pymunk.Body.STATIC)
    base.position = (screen_width // 2, screen_height + 25)
    base_shape = pymunk.Poly.create_box(base, (screen_width, 50))
    base_shape.friction = 0.2
    space.add(base, base_shape)

    wall_left = pymunk.Body(mass=10 ** 5, moment=0, body_type=pymunk.Body.STATIC)
    wall_left.position = (-50, screen_height // 2)
    wall_left_shape = pymunk.Poly.create_box(wall_left, (100, screen_height))
    space.add(wall_left, wall_left_shape)

    wall_right = pymunk.Body(mass=10 ** 5, moment=0, body_type=pymunk.Body.STATIC)
    wall_right.position = (screen_width + 50, screen_height // 2)
    wall_right_shape = pymunk.Poly.create_box(wall_right, (100, screen_height))
    space.add(wall_right, wall_right_shape)

def move_left_to_right(audio,speed ,dt):
    """
    Function to move an object from left to right in pymunk space
    """
    position = audio.get_position()
    x = position[0] + (speed * dt)
    audio.set_position((x, position[1], position[2]))
    if x >= 20.0:
        audio.is_moving = False
        audio.stop()

def on_gaviota_move(gaviota):
    """
    Function to handle gaviota movement in pymunk space
    """
    gaviota.set_position((-10.0, 0.0, 3.0))
    gaviota.is_moving = True
    gaviota.play()

def rain(list, space, num_balls):
    """
    Function to simulate rain by creating rocks in pymunk space
    """
    num = randint(5, num_balls)
    w, h = pygame.display.get_surface().get_size()
    for i in range(0, num):
        rock = create_rock(space, randint(0, w), randint(15, 50))
        list.append(rock)

def start_game():
    """
    Main function that starts the game loop
    """
    gaviota_speed = 1.7
    start_cross_to_personas = False
    start_cross_to_fondo = False
    start_cross_to_storm = False

    fondo_volumen = 0.3
    personas_volumen = 0.15
    storm_volumen = 0.15

    fondo = AudioPlayer("./data/fondo.wav", "Fondo")
    personas = AudioPlayer("./data/personas.wav", "Personas")
    storm = AudioPlayer("./data/tormenta.wav", "Tormenta")

    gaviota = AudioPlayer("./data/gaviota.wav", "Gaviota")

    fondo.set_looping(True)
    personas.set_looping(True)
    storm.set_looping(True)

    raining = False
    raining_timer = 0.0
    num_raining = 0

    personas.set_gain(0.0)
    personas.play()

    # storm gain target 0.05
    storm.set_gain(0.0)
    storm.play()
    

    gaviota.show_imgui(dpg, True)
    gaviota.set_gain(5.0)

    #gaviota.play()
    fondo.play()
    fondo.set_gain(0.3)

    actual_sound = fondo


    global USE_PYMUNK, SMOOTH, VOLUME_RISE, TEXTURE, DISPLAY_HELP
    if USE_PYMUNK:
        create_walls()
    
    wave = Wave()
    s = pygame.Surface(screen.get_size(), pygame.SRCALPHA).convert_alpha()
    objects: list[pymunk.Circle] = []
    floating_objects: list[Ball] = []

    floating_objects.append(Ball(50, 10))
    last_time = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_time) / 1000.0
        last_time = current_time
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    sys.exit(0)
                if e.key == pygame.K_s:
                    SMOOTH = not SMOOTH
                if e.key == pygame.K_v:
                    VOLUME_RISE = not VOLUME_RISE
                if e.key == pygame.K_p:
                    USE_PYMUNK = not USE_PYMUNK
                if e.key == pygame.K_t:
                    TEXTURE = not TEXTURE
                if e.key == pygame.K_h:
                    DISPLAY_HELP = not DISPLAY_HELP
                if e.key == pygame.K_q:
                    gaviota.set_position((-10.0, 0.0, 3.0))
                    gaviota.play()
                    gaviota.is_moving = True

                if e.key == pygame.K_w:
                    print("Raining!")
                    raining = True
                    num_raining = 10
                    if not b.is_chill():
                        b.change_state()
                    start_cross_to_fondo = True
                if e.key == pygame.K_e:
                    print("Strom!")
                    num_raining = 20
                    raining = True
                    if b.is_chill():
                        b.change_state()
                    start_cross_to_storm = True

                if e.key == pygame.K_SPACE:
                    print("change state")
                    b.change_state()

                if e.key == pygame.K_a:
                    print("cross de fondo a personas")
                    raining = False
                    if not b.is_chill():
                        b.change_state()
                    start_cross_to_personas = True
                    
                if e.key == pygame.K_s:
                    print("cross de personas a fondo")
                    raining = False
                    if not b.is_chill():
                        b.change_state()
                    start_cross_to_fondo = True


            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1 and USE_PYMUNK:
                    mx, my = pygame.mouse.get_pos()
                    rock = create_rock(space, mx, my)
                    objects.append(rock)
        if USE_PYMUNK:
            space.step(1 / FPS)
        screen.fill('black')
        s.fill(0)
        for i in objects:
            if not i.body.splashed:
                if i.body.position.y + i.radius > wave.get_target_height():
                    i.body.splashed = True
                    wave.splash(index=wave.get_spring_index_for_x_pos(i.body.position.x), vel=i.radius)
                    if VOLUME_RISE:
                        #wave.add_volume(i.radius ** 2 * math.pi)
                        pass
            else:
                space.remove(i)
                objects.remove(i)
        
            draw_rock(i, screen)
        for i in floating_objects:
            i.update()
            i.draw(screen)
            index = wave.get_spring_index_for_x_pos(i.x)
            if i.y > wave.get_target_height():
                if not i.spring:
                    i.spring = wave.springs[index]
                    try:
                        i.next_spring = wave.springs[index + 1]
                    except IndexError:
                        pass
                    wave.splash(index, 2)
        wave.update()
        wave.draw(s)
        screen.blit(s, (0, 0))
        wave.draw_line(screen)
        if DISPLAY_HELP:
            display_help()
        pygame.display.update()

        # Si no se esta moviendo sacamos random

        #if gaviota.is_moving == False:
            #num_rand = randint(1, 500)
            #if num_rand == 5:
                #on_gaviota_move(gaviota)
                #print("Vengaaa la gaviota")
        if(start_cross_to_personas == True):
            if fondo.get_gain() > 0.0:
                start_cross_to_personas = cross_fade(fondo, personas, personas_volumen,delta_time)
            else:
                start_cross_to_personas = cross_fade(storm, personas, personas_volumen,delta_time)
            

        if(start_cross_to_fondo == True):
            if personas.get_gain() > 0.0:
                start_cross_to_fondo = cross_fade(personas, fondo, fondo_volumen,delta_time)
            else:
                start_cross_to_fondo = cross_fade(storm, fondo, fondo_volumen,delta_time)

        if(start_cross_to_storm == True):
            if fondo.get_gain() > 0.0:
                start_cross_to_storm = cross_fade(fondo, storm, storm_volumen, delta_time)
            else:
                start_cross_to_storm = cross_fade(personas, storm, storm_volumen, delta_time)
       

        if (raining):
            raining_timer += delta_time
            if (raining_timer >= 1.0):
                raining_timer -= 1.0
                rain(objects, space, num_raining)

                
        if gaviota.is_moving == True:
            move_left_to_right(gaviota, gaviota_speed, delta_time)
        

        #print(b)
       
        
        b.update()        
        clock.tick(FPS)

def main_game():
    """
    Main pygame loop and calling start_game in a separate thread
    """
    oalInit()
    listener = oalGetListener()
    listener.set_position((10.0, 0.0, 0.0))

    

    # Imgui context
    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    #fondo.show_imgui(dpg)
    #gaviota.show_imgui(dpg)
    #gaviota.update_source_position()
    

    thread_game = threading.Thread(target=start_game)
    thread_game.start()
    

    """
    with dpg.window(label="Example Window"):
      dpg.add_text("Hello world")
      #dpg.add_button(label="Save", callback=save_callback)
      dpg.add_input_text(label="string")
      dpg.add_slider_float(label="float")
    """


    print("hola")

    dpg.show_viewport()
    dpg.start_dearpygui()
    #while dpg.is_dearpygui_running():
    while True:
      dpg.render_dearpygui_frame()
      
        
        #audio.show_effect_buttons()

      
      # print(clock.get_fps())

# Call to main_game to start the program
main_game()
# Wait for the start_game thread to finish before destroying the ImGui context
thread_game.join()
dpg.destroy_context()