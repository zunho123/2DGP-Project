from pico2d import *
import game_framework
from stage import Stage
from player import Player

stage = None
player = None
move_dir = 0
left_pressed = False
right_pressed = False

PLAYER_SCALE_STAGE0 = 1.5

def enter():
    global stage, player, move_dir, left_pressed, right_pressed
    w = get_canvas_width()
    h = get_canvas_height()
    stage = Stage('stage0.png', window_w=w, window_h=h, zoom=2.0, ground_px= -12.5)
    stage.platforms = [(0, stage.w, stage.ground_y)]
    player = Player(stage, scale=PLAYER_SCALE_STAGE0)
    move_dir = 0
    left_pressed = False
    right_pressed = False

def exit():
    global stage, player
    stage = None
    player = None

def handle_events(events):
    global left_pressed, right_pressed
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()
            elif e.key == SDLK_LEFT:
                left_pressed = True
            elif e.key == SDLK_RIGHT:
                right_pressed = True
            elif e.key == SDLK_SPACE:
                player.request_jump()
            elif e.key == SDLK_a:
                player.request_attack()
            elif e.key == SDLK_s:
                player.request_roll()
        elif e.type == SDL_KEYUP:
            if e.key == SDLK_LEFT:
                left_pressed = False
            elif e.key == SDLK_RIGHT:
                right_pressed = False

def update(dt):
    global move_dir
    move_dir = 0
    if left_pressed:
        move_dir -= 1
    if right_pressed:
        move_dir += 1
    player.update(dt, move_dir)
    stage.update(dt, player.x)

def draw():
    clear_canvas()
    stage.draw()
    player.draw()
    update_canvas()
