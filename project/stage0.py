from pico2d import *
import game_framework
from stage import Stage
from player import Player
from enemy import EN_DEAD

stage = None
player = None
move_dir = 0
left_pressed = False
right_pressed = False
up_hint = None
can_use_elevator = False
enemies = []
elevator_used = False

PLAYER_SCALE_STAGE0 = 1.5
FIRST_FLOOR_GROUND = -12.5
FIRST_FLOOR_START_X = 1350

ELEVATOR_X = 380
ELEVATOR_RANGE = 40
GROUND_TOLERANCE = 8

SECOND_FLOOR_GROUND = 242
SECOND_FLOOR_START_X = 80


def enter():
    global stage, player, move_dir, left_pressed, right_pressed
    global up_hint, can_use_elevator, enemies, elevator_used

    w = get_canvas_width()
    h = get_canvas_height()

    stage = Stage('stage0.png', window_w=w, window_h=h, zoom=2.0, ground_px=FIRST_FLOOR_GROUND)
    stage.platforms = [(0, stage.w, stage.ground_y)]

    player = Player(stage, scale=PLAYER_SCALE_STAGE0)
    player.x = FIRST_FLOOR_START_X
    player.dir = -1

    move_dir = 0
    left_pressed = False
    right_pressed = False

    up_hint = load_image('upkey.png')
    can_use_elevator = False
    enemies = []
    elevator_used = False


def exit():
    global stage, player, up_hint, enemies, can_use_elevator, elevator_used
    stage = None
    player = None
    up_hint = None
    enemies = []
    can_use_elevator = False
    elevator_used = False


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
            elif e.key == SDLK_UP:
                if can_use_elevator:
                    move_to_second_floor()
        elif e.type == SDL_KEYUP:
            if e.key == SDLK_LEFT:
                left_pressed = False
            elif e.key == SDLK_RIGHT:
                right_pressed = False


def all_enemies_dead():
    if not enemies:
        return True
    for e in enemies:
        if getattr(e, 'state', None) != EN_DEAD:
            return False
    return True


def near_elevator():
    if stage is None or player is None:
        return False
    if elevator_used:
        return False
    if abs(player.y - FIRST_FLOOR_GROUND) > GROUND_TOLERANCE:
        return False
    return ELEVATOR_X - ELEVATOR_RANGE <= player.x <= ELEVATOR_X + ELEVATOR_RANGE


def move_to_second_floor():
    global can_use_elevator, elevator_used

    stage.ground_y = SECOND_FLOOR_GROUND
    stage.platforms = [(0, stage.w, stage.ground_y)]

    player.x = SECOND_FLOOR_START_X
    player.y = stage.ground_y + player.ground_off
    player.vy = 0
    player.on_ground = True
    player.dir = 1

    can_use_elevator = False
    elevator_used = True


def update(dt):
    global move_dir, can_use_elevator
    move_dir = 0
    if left_pressed:
        move_dir -= 1
    if right_pressed:
        move_dir += 1

    player.update(dt, move_dir)
    stage.update(dt, player.x)

    can_use_elevator = all_enemies_dead() and near_elevator()


def draw():
    clear_canvas()
    stage.draw()
    player.draw()
    if can_use_elevator and up_hint is not None:
        sx, sy = stage.to_screen(player.x, player.y)
        size = 50
        up_hint.draw(sx, sy + 175, size, size)
    update_canvas()
