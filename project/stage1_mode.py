from pico2d import *
import game_framework
from stage import Stage
from player import Player
import logo_mode

stage = None
player = None
move_dir = 0
left_pressed = False
right_pressed = False
bgm = None

PLAYER_SCALE_STAGE1_2 = 2.0
STAGE_CLEAR_DELAY = 2.0
STAGE_CLEAR_WAIT = 2.0
STAGE_CLEAR_FONT_SIZE = 72

stage_clear = False
stage_clear_time = 0.0
stage_clear_font = None

def enter():
    global stage, player, move_dir, left_pressed, right_pressed, bgm
    global stage_clear, stage_clear_time, stage_clear_font

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

    stage_clear = False
    stage_clear_time = 0.0
    stage_clear_font = load_font('neodgm.ttf', STAGE_CLEAR_FONT_SIZE)


def exit():
    global bgm
    global stage_clear, stage_clear_time, stage_clear_font

    if bgm is not None:
        bgm.stop()
    bgm = None

    stage_clear = False
    stage_clear_time = 0.0
    stage_clear_font = None

def handle_events(events):
    global move_dir, left_pressed, right_pressed
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()
            elif e.key == SDLK_q:
                game_framework.change_to_loading()
                return
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
    global move_dir, stage_clear, stage_clear_time

    stage_clear_time += dt
    if (not stage_clear) and stage_clear_time >= STAGE_CLEAR_DELAY:
        stage_clear = True

    if stage_clear and stage_clear_time >= STAGE_CLEAR_DELAY + STAGE_CLEAR_WAIT:
        game_framework.change_state(logo_mode)
        return

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

    if stage_clear and stage_clear_font is not None:
        w = get_canvas_width()
        h = get_canvas_height()
        cx = w // 2
        cy = h // 2
        text = 'STAGE CLEAR'
        approx_half = len(text) * STAGE_CLEAR_FONT_SIZE * 0.3
        stage_clear_font.draw(cx - approx_half, cy, text, (255, 255, 0))

    update_canvas()

