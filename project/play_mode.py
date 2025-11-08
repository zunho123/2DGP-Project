from pico2d import *
import game_framework
from stage import Stage
from player import Player
from enemy import Enemy

stage = None
player = None
enemy = None
move_dir = 0

def enter():
    global stage, player, enemy
    stage = Stage('stage1.png', window_w=1280, window_h=720, zoom=1.6, ground_px=36)
    player = Player(stage, scale=1.0)
    enemy = Enemy(stage, scale=0.9)

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
    enemy.update(dt)
    stage.update(dt, player.x)

def draw():
    clear_canvas()
    stage.draw()
    enemy.draw()
    player.draw()
    update_canvas()
