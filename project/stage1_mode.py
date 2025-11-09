from pico2d import *
import game_framework
from stage import Stage
from player import Player

stage = None
player = None
move_dir = 0

def enter():
    global stage, player, move_dir
    stage = Stage('stage1-2.png', window_w=1280, window_h=720, zoom=4.0, ground_px=18)
    player = Player(stage)
    player.x = 40
    player.y = stage.ground_y
    move_dir = 0
    stage.update(0.0, player.x)

def exit():
    pass

def handle_events(events):
    global move_dir
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()
            elif e.key == SDLK_LEFT:
                move_dir -= 1
            elif e.key == SDLK_RIGHT:
                move_dir += 1
            elif e.key == SDLK_SPACE:
                player.request_jump()
            elif e.key == SDLK_a:
                player.request_attack()
        elif e.type == SDL_KEYUP:
            if e.key == SDLK_LEFT:
                move_dir += 1
            elif e.key == SDLK_RIGHT:
                move_dir -= 1

def update(dt):
    player.update(dt, move_dir)
    stage.update(dt, player.x)

def draw():
    clear_canvas()
    stage.draw()
    player.draw()
    update_canvas()
