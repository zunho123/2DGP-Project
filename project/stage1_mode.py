from pico2d import *
import game_framework
from stage import Stage
from player import Player

stage = None
player = None
move_dir = 0
left_pressed = False
right_pressed = False
bgm = None

PLAYER_SCALE_STAGE1_2 = 2.0

def enter():
    global stage, player, move_dir, left_pressed, right_pressed, bgm
    stage = Stage('stage1-2.png', window_w=1920, window_h=1080, zoom=1.0, ground_px=220)
    player = Player(stage, scale=PLAYER_SCALE_STAGE1_2)
    player.x = 580
    player.y = stage.ground_y + player.ground_off + 2
    move_dir = 0
    left_pressed = False
    right_pressed = False
    target = stage.clamp(player.x - stage.vw * 0.5, 0, max(0, stage.w - stage.vw))
    stage.cam_x = target
    bgm = load_music('song_rooftop.ogg')
    bgm.set_volume(64)
    bgm.repeat_play()

def exit():
    global bgm
    if bgm is not None:
        bgm.stop()
    bgm = None

def handle_events(events):
    global move_dir, left_pressed, right_pressed
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
