from pico2d import *
import time
from stage import Stage
from player import Player
from enemy import Enemy

name = 'play_mode'

stage = None
player = None
enemy = None

left_pressed = False
right_pressed = False
running = True
last_time = 0.0

def enter():
    global stage, player, enemy, last_time
    open_canvas(1280, 720)
    stage = Stage('stage1.png', 1280, 720)
    player = Player(stage)
    enemy = Enemy(stage, player.x + 220)
    last_time = time.time()

def exit():
    close_canvas()

def pause():
    pass

def resume():
    pass

def handle_events():
    global left_pressed, right_pressed, running
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            running = False
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                running = False
            elif e.key == SDLK_LEFT:
                left_pressed = True
            elif e.key == SDLK_RIGHT:
                right_pressed = True
            elif e.key == SDLK_SPACE:
                player.request_jump()
            elif e.key == SDLK_a:
                player.request_attack()
        elif e.type == SDL_KEYUP:
            if e.key == SDLK_LEFT:
                left_pressed = False
            elif e.key == SDLK_RIGHT:
                right_pressed = False
    player.input_axis(-1 if left_pressed else 0, 1 if right_pressed else 0)

def update():
    global last_time
    now = time.time()
    dt = now - last_time
    last_time = now
    player.update(dt)
    enemy.update(dt)
    if enemy.alive and player.attack_active() and player.attack_hit(enemy.get_bb()):
        enemy.kill()
    stage.set_view_by_center(player.x)

def draw():
    clear_canvas()
    stage.draw()
    enemy.draw()
    player.draw()
    update_canvas()

def get_running():
    return running
