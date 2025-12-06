from pico2d import *
import game_framework
from stage import Stage
from player import Player
from enemy import EN_DEAD
from snow import Snow
import logo_mode

stage = None
player = None
move_dir = 0
left_pressed = False
right_pressed = False
up_hint = None
can_use_elevator = False
enemies = []
elevator_used = False
paused = True
hint_font = None
tutorial_step = 0

stage_clear = False
stage_clear_time = 0.0
stage_clear_font = None
bgm = None

PLAYER_SCALE_STAGE0 = 1.5
FIRST_FLOOR_GROUND = -12.5
FIRST_FLOOR_START_X = 1350

ELEVATOR_X = 380
ELEVATOR_RANGE = 40
GROUND_TOLERANCE = 8

SECOND_FLOOR_GROUND = 242
SECOND_FLOOR_START_X = 80

ATTACK_TUTORIAL_X = 950
ROLL_TUTORIAL_X = 650

STAGE_CLEAR_WAIT = 2.0
STAGE_CLEAR_FONT_SIZE = 72


def enter():
    global stage, player, move_dir, left_pressed, right_pressed
    global up_hint, can_use_elevator, enemies, elevator_used, paused, hint_font, tutorial_step
    global stage_clear, stage_clear_time, stage_clear_font, bgm

    w = get_canvas_width()
    h = get_canvas_height()

    stage = Stage('stage0.png', window_w=w, window_h=h, zoom=2.0, ground_px=FIRST_FLOOR_GROUND)
    stage.platforms = [(0, stage.w, stage.ground_y)]

    player = Player(stage, scale=PLAYER_SCALE_STAGE0)
    player.x = FIRST_FLOOR_START_X
    player.dir = -1

    target = stage.clamp(player.x - stage.vw * 0.5, 0, max(0, stage.w - stage.vw))
    stage.cam_x = target

    move_dir = 0
    left_pressed = False
    right_pressed = False

    up_hint = load_image('upkey.png')
    can_use_elevator = False
    enemies = []
    snow = Snow(stage, scale=1.0)
    snow.x = 900
    enemies.append(snow)

    elevator_used = False

    hint_font = load_font('neodgm.ttf', 20)
    paused = True
    tutorial_step = 0

    stage_clear = False
    stage_clear_time = 0.0
    stage_clear_font = load_font('neodgm.ttf', STAGE_CLEAR_FONT_SIZE)

    bgm = load_music('song_neon.mp3')
    bgm.set_volume(64)
    bgm.repeat_play()


def rect_overlap(l1, b1, r1, t1, l2, b2, r2, t2):
    return not (r1 < l2 or r2 < l1 or t1 < b2 or t2 < b1)


def exit():
    global stage, player, up_hint, enemies, can_use_elevator, elevator_used
    global hint_font, paused, tutorial_step
    global stage_clear, stage_clear_time, stage_clear_font, bgm

    stage = None
    player = None
    up_hint = None
    enemies = []
    can_use_elevator = False
    elevator_used = False
    hint_font = None
    paused = True
    tutorial_step = 0

    stage_clear = False
    stage_clear_time = 0.0
    stage_clear_font = None

    if bgm is not None:
        bgm.stop()
    bgm = None


def handle_events(events):
    global left_pressed, right_pressed, paused, tutorial_step
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()

            if paused:
                if tutorial_step == 0:
                    if e.key == SDLK_LEFT:
                        paused = False
                        left_pressed = True
                    elif e.key == SDLK_RIGHT:
                        paused = False
                        right_pressed = True
                    elif e.key == SDLK_SPACE:
                        paused = False
                        player.request_jump()
                    else:
                        paused = False
                    return
                elif tutorial_step == 1:
                    if e.key == SDLK_a:
                        paused = False
                        player.request_attack()
                    return
                elif tutorial_step == 2:
                    if e.key == SDLK_s:
                        paused = False
                        player.request_roll()
                        for obj in enemies:
                            if hasattr(obj, 'start_attack'):
                                obj.start_attack(player.x, player.dir)
                                break
                    return

            if e.key == SDLK_LEFT:
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
            if paused:
                continue
            if e.key == SDLK_LEFT:
                left_pressed = False
            elif e.key == SDLK_RIGHT:
                right_pressed = False


def all_enemies_dead():
    if not enemies:
        return True
    for e in enemies:
        if hasattr(e, 'is_dead'):
            if not e.is_dead():
                return False
        else:
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
    global can_use_elevator, elevator_used, stage_clear, stage_clear_time

    stage.ground_y = SECOND_FLOOR_GROUND
    stage.platforms = [(0, stage.w, stage.ground_y)]

    player.x = SECOND_FLOOR_START_X
    player.y = stage.ground_y + player.ground_off
    player.vy = 0
    player.on_ground = True
    player.dir = 1

    target = stage.clamp(player.x - stage.vw * 0.5, 0, max(0, stage.w - stage.vw))
    stage.cam_x = target

    can_use_elevator = False
    elevator_used = True
    stage_clear = True
    stage_clear_time = 0.0


def update(dt):
    global move_dir, can_use_elevator, tutorial_step, left_pressed, right_pressed, paused
    global stage_clear, stage_clear_time

    if stage_clear:
        stage_clear_time += dt
        if stage_clear_time >= STAGE_CLEAR_WAIT:
            game_framework.change_state(logo_mode)
            return

    if paused:
        can_use_elevator = False
        return

    move_dir = 0
    if left_pressed:
        move_dir -= 1
    if right_pressed:
        move_dir += 1

    player.update(dt, move_dir)
    for e in enemies:
        e.update(dt)
    stage.update(dt, player.x)

    if tutorial_step == 0 and player.x <= ATTACK_TUTORIAL_X:
        paused = True
        tutorial_step = 1
        move_dir = 0
        left_pressed = False
        right_pressed = False
        return

    if tutorial_step == 1 and player.x <= ROLL_TUTORIAL_X:
        paused = True
        tutorial_step = 2
        move_dir = 0
        left_pressed = False
        right_pressed = False
        return

    if tutorial_step >= 1:
        if hasattr(player, 'is_attacking_active') and hasattr(player, 'attack_hitbox'):
            if player.is_attacking_active():
                l1, b1, r1, t1 = player.attack_hitbox()
                for obj in enemies:
                    if hasattr(obj, 'is_dead') and obj.is_dead():
                        continue
                    if hasattr(obj, 'get_bb'):
                        l2, b2, r2, t2 = obj.get_bb()
                        if rect_overlap(l1, b1, r1, t1, l2, b2, r2, t2):
                            if hasattr(obj, 'die'):
                                obj.die()

    can_use_elevator = all_enemies_dead() and near_elevator()


def draw():
    clear_canvas()
    stage.draw()
    for e in enemies:
        e.draw()
    player.draw()

    if can_use_elevator and up_hint is not None:
        sx, sy = stage.to_screen(player.x, player.y)
        size = 50
        up_hint.draw(sx, sy + 175, size, size)

    if paused and hint_font is not None:
        sx, sy = stage.to_screen(player.x, player.y)
        if tutorial_step == 0:
            hint_font.draw(sx - 100, sy + 230, '<- / -> : 이동', (255, 255, 255))
            hint_font.draw(sx - 100, sy + 210, 'SPACE : 점프', (255, 255, 255))
            hint_font.draw(sx - 100, sy + 190, '아무 키를 눌러 계속', (255, 255, 0))
        elif tutorial_step == 1:
            hint_font.draw(sx - 100, sy + 230, 'A : 공격', (255, 255, 255))
            hint_font.draw(sx - 100, sy + 210, '공격 해 처리하세요.', (255, 255, 0))
        elif tutorial_step == 2:
            hint_font.draw(sx - 100, sy + 230, 'S : 구르기', (255, 255, 255))
            hint_font.draw(sx - 100, sy + 210, '굴러 공격을 회피하세요.', (255, 255, 0))

    if stage_clear and stage_clear_font is not None:
        w = get_canvas_width()
        h = get_canvas_height()
        cx = w // 2
        cy = h // 2
        text = 'STAGE CLEAR'
        approx_half = len(text) * STAGE_CLEAR_FONT_SIZE * 0.3
        stage_clear_font.draw(cx - approx_half, cy, text, (255, 255, 0))

    update_canvas()
