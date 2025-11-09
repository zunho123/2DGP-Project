from pico2d import *
import game_framework
from stage import Stage
from player import Player
from enemy import Enemy

stage = None
player = None
enemy = None
move_dir = 0

def rect_overlap(l1,b1,r1,t1,l2,b2,r2,t2):
    return not (r1 < l2 or r2 < l1 or t1 < b2 or t2 < b1)

def enter():
    global stage, player, enemy, move_dir
    stage = Stage('stage1.png', window_w=1280, window_h=720, zoom=4.0, ground_px=15)
    player = Player(stage)
    enemy = Enemy(stage)
    move_dir = 0

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
    if enemy.is_alive() and player.is_attacking_active():
        l1,b1,r1,t1 = player.attack_hitbox()
        l2,b2,r2,t2 = enemy.aabb()
        if rect_overlap(l1,b1,r1,t1,l2,b2,r2,t2):
            enemy.die()
    enemy.update(dt)
    stage.update(dt, player.x)

def draw():
    clear_canvas()
    stage.draw()
    enemy.draw()
    player.draw()
    update_canvas()
