from pico2d import *
import time
from stage import Stage
from player import Player
from enemy import Enemy

WINDOW_W, WINDOW_H = 1280, 720

stage = None
player = None
enemy = None
last_time = 0.0

left_pressed = False
right_pressed = False
running = True

def enter():
    global stage, player, enemy, last_time
    open_canvas(WINDOW_W, WINDOW_H)
    stage = Stage('stage1.png', WINDOW_W, WINDOW_H, zoom_mul=1.4, ground_ratio=0.0, ground_px=22, snap=6.0)
    player = Player(stage)
    enemy = Enemy(stage, player.x + 160)
    enemy.dir = -1
    last_time = time.time()

def exit():
    close_canvas()

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

def update():
    global last_time
    now = time.time()
    dt = now - last_time
    last_time = now

    move_dir = (-1 if left_pressed else 0) + (1 if right_pressed else 0)
    player.update(dt, move_dir)
    enemy.update(dt, 0)

    player.ground_y = stage.ground_y + player.ground_off
    enemy.ground_y = stage.ground_y + enemy.ground_off

    lead = 120 if player.dir == 1 else -120
    stage.set_view_follow(player.x, dt, lead_px=lead)

def draw():
    clear_canvas()
    stage.draw()
    enemy.draw(stage)
    player.draw(stage)
    update_canvas()

def pause():
    pass

def resume():
    pass

def run():
    enter()
    global running
    while running:
        handle_events()
        update()
        draw()
        delay(0.001)
    exit()

if __name__ == "__main__":
    run()
