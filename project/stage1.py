from pico2d import *
import game_framework
import stage1_mode
from stage import Stage
from player import Player, DEAD
from enemy import Enemy, EN_SPECIAL
from kill_effect import KillSlashEffect
from blood_effect import BloodEffect

stage = None
player = None
enemy = None
move_dir = 0
up_hint = None
can_enter_next = False
bgm = None
hint_font = None
effects = []
boss_hp_font = None
warning_img = None

TRIGGER_X_MAX = 120
PROMPT_SIZE = 56
PLAYER_SCALE_STAGE1 = 1.0
GAME_OVER_DELAY = 1.0
RESTART_DELAY = 3.0
GAME_OVER_FONT_SIZE = 72
RESTART_FONT_SIZE = 36

SLOWMO_DURATION = 1.0
SLOWMO_SCALE = 0.25

game_over_font = None
restart_font = None
slowmo_time = 0.0

game_over_font = None
restart_font = None



def rect_overlap(l1, b1, r1, t1, l2, b2, r2, t2):
    return not (r1 < l2 or r2 < l1 or t1 < b2 or t2 < b1)


def enter():
    global stage, player, enemy, up_hint, move_dir, can_enter_next, bgm, effects
    global game_over_font, restart_font, death_count, tutorial_paused, last_player_state, hint_font, boss_hp_font, warning_img
    global player_attack_active_prev, enemy_damaged_this_attack
    global slowmo_time
    stage = Stage('stage1.png', window_w=1920, window_h=1080, zoom=4.0, ground_px=15)
    player = Player(stage, scale=PLAYER_SCALE_STAGE1)
    enemy = Enemy(stage)
    up_hint = load_image('upkey.png')
    move_dir = 0
    can_enter_next = False
    effects = []
    bgm = load_music('song_boss1.ogg')
    bgm.set_volume(64)
    bgm.repeat_play()
    game_over_font = load_font('neodgm.ttf', GAME_OVER_FONT_SIZE)
    restart_font = load_font('neodgm.ttf', RESTART_FONT_SIZE)
    hint_font = load_font('neodgm.ttf', 24)
    boss_hp_font = load_font('neodgm.ttf', 20)
    warning_img = load_image('warning.png')
    death_count = 0
    tutorial_paused = True
    last_player_state = player.state
    player_attack_active_prev = False
    enemy_damaged_this_attack = False
    slowmo_time = 0.0

def exit():
    global bgm, game_over_font, restart_font, death_count, tutorial_paused, last_player_state, hint_font, boss_hp_font, warning_img
    global player_attack_active_prev, enemy_damaged_this_attack
    global slowmo_time
    if bgm is not None:
        bgm.stop()
    bgm = None
    game_over_font = None
    restart_font = None
    hint_font = None
    death_count = 0
    tutorial_paused = False
    last_player_state = None
    boss_hp_font = None
    player_attack_active_prev = False
    enemy_damaged_this_attack = False
    warning_img = None
    slowmo_time = 0.0

def restart_play():
    global move_dir, last_player_state, player_attack_active_prev, enemy_damaged_this_attack
    if player is None or stage is None:
        return
    player.start_stand()
    player.y = stage.ground_y + player.ground_off + 2
    player.vy = 0.0
    player.on_ground = True
    player.hit_flash_timer = 0.0
    move_dir = 0
    last_player_state = player.state
    player_attack_active_prev = False
    enemy_damaged_this_attack = False


def handle_events(events):
    global move_dir, can_enter_next, tutorial_paused
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()
                continue
            elif e.key == SDLK_q:
                if hasattr(game_framework, 'change_to_loading'):
                    game_framework.change_to_loading()
                continue

            if tutorial_paused:
                tutorial_paused = False
                move_dir = 0

            if player is not None and player.state == DEAD:
                if hasattr(player, 'dead_time') and player.dead_time >= RESTART_DELAY:
                    if e.key == SDLK_r:
                        restart_play()
                continue

            if e.key == SDLK_LEFT:
                move_dir -= 1
            elif e.key == SDLK_RIGHT:
                move_dir += 1
            elif e.key == SDLK_SPACE:
                player.request_jump()
            elif e.key == SDLK_a:
                player.request_attack()
            elif e.key == SDLK_s:
                player.request_roll()
            elif e.key == SDLK_UP:
                if can_enter_next:
                    game_framework.change_state(stage1_mode)

        elif e.type == SDL_KEYUP:
            if e.key == SDLK_LEFT:
                move_dir += 1
            elif e.key == SDLK_RIGHT:
                move_dir -= 1


def _enemy_dead():
    if enemy is None:
        return True
    if hasattr(enemy, 'is_dead'):
        return enemy.is_dead()
    if hasattr(enemy, 'is_alive'):
        return not enemy.is_alive()
    return False


def update(dt):
    global can_enter_next, effects, death_count, last_player_state, tutorial_paused
    global player_attack_active_prev, enemy_damaged_this_attack
    global slowmo_time
    if tutorial_paused:
        return

    if player is None:
        return

    if last_player_state is None:
        last_player_state = player.state

    local_dt = dt
    if slowmo_time > 0.0:
        slowmo_time -= dt
        if slowmo_time < 0.0:
            slowmo_time = 0.0
        local_dt = dt * SLOWMO_SCALE

    prev_state = last_player_state

    player.update(local_dt, move_dir)

    attack_active = hasattr(player, 'is_attacking_active') and player.is_attacking_active()
    if attack_active and not player_attack_active_prev:
        enemy_damaged_this_attack = False

    if enemy:
        if hasattr(enemy, 'is_alive') and enemy.is_alive():
            if attack_active:
                l1, b1, r1, t1 = player.attack_hitbox()
                l2, b2, r2, t2 = enemy.aabb()
                if rect_overlap(l1, b1, r1, t1, l2, b2, r2, t2):
                    if not enemy_damaged_this_attack:
                        prev_hp = enemy.hp
                        was_alive = enemy.is_alive()
                        enemy.take_damage()
                        enemy_damaged_this_attack = True
                        ex = (l2 + r2) * 0.5
                        ey = (b2 + t2) * 0.5
                        dir = player.dir if hasattr(player, 'dir') else 1
                        if was_alive and (enemy.hp <= 0 or not enemy.is_alive()):
                            slowmo_time = SLOWMO_DURATION
                            effects.append(KillSlashEffect(stage, ex, ey, dir, scale=1.0))
                        else:
                            effects.append(BloodEffect(stage, ex, ey, scale=0.1))
        enemy.update(local_dt)

    for eff in effects:
        eff.update(local_dt)
    effects[:] = [e for e in effects if e.is_alive()]

    stage.update(local_dt, player.x)

    near_stairs = (player.x <= TRIGGER_X_MAX) and abs(player.y - stage.ground_y) < 8
    can_enter_next = _enemy_dead() and near_stairs

    if prev_state != DEAD and player.state == DEAD:
        death_count += 1

    last_player_state = player.state
    player_attack_active_prev = attack_active


def draw():
    clear_canvas()
    stage.draw()
    if enemy:
        enemy.draw()

        if boss_hp_font is not None and hasattr(enemy, 'hp') and hasattr(enemy, 'is_alive') and enemy.is_alive():
            sx, sy = stage.to_screen(enemy.x, enemy.y)
            current_hp = max(enemy.hp, 0)
            text = f'HP: {current_hp}/{enemy.max_hp}'
            box_w = int(len(text) * 14)
            box_h = 32
            box_x = sx
            box_y = sy + 10
            left = box_x - box_w // 2
            right = box_x + box_w // 2
            bottom = box_y - box_h // 2
            top = box_y + box_h // 2
            boss_hp_font.draw(left + 10, box_y - 10, text, (255, 0, 0))

    for eff in effects:
        eff.draw()
    player.draw()

    if warning_img is not None and enemy is not None and player is not None:
        if hasattr(enemy, 'state') and enemy.state == EN_SPECIAL:
            sx, sy = stage.to_screen(player.x, player.y)
            wy = sy + int(80 * stage.zoom)
            warning_img.draw(sx, wy, 96, 96)

    if can_enter_next and up_hint is not None:
        sx, sy = stage.to_screen(player.x, player.y)
        up_hint.draw(sx, sy + int(80 * stage.zoom), PROMPT_SIZE, PROMPT_SIZE)

    if hint_font is not None:
        w = get_canvas_width()
        h = get_canvas_height()
        hint_font.draw(10, h - 30, 'q : 로딩 화면 전환', (255, 255, 255))
        if tutorial_paused:
            cx = w // 2
            cy = h // 2
            box_w = int(w * 0.7)
            box_h = 110
            left = cx - box_w // 2
            right = cx + box_w // 2
            bottom = cy - box_h // 2
            top = cy + box_h // 2
            hint_font.draw(left + 100, cy + 390, '보스를 공격해도 그의 공격은 끊기지 않습니다.', (255, 255, 255))
            hint_font.draw(left + 100, cy + 360, '타이밍을 잘 잡으세요.', (255, 255, 255))
            hint_font.draw(left + 100, cy + 330, '아무 키를 눌러 계속', (255, 255, 0))

    if player is not None and hasattr(player, 'dead_time') and player.state == DEAD:
        if game_over_font is not None and player.dead_time >= GAME_OVER_DELAY:
            w = get_canvas_width()
            h = get_canvas_height()
            cx = w // 2
            cy = h // 2
            text = "GAME OVER"
            approx_half = len(text) * GAME_OVER_FONT_SIZE * 0.3
            game_over_font.draw(cx - approx_half,
                                cy,
                                text)
        if restart_font is not None and player.dead_time >= RESTART_DELAY:
            w = get_canvas_width()
            h = get_canvas_height()
            cx = w // 2
            cy = h // 2
            text2 = "RESTART? : R/r"
            approx_half2 = len(text2) * RESTART_FONT_SIZE * 0.3
            restart_y = cy - RESTART_FONT_SIZE
            restart_font.draw(cx - approx_half2,
                              restart_y,
                              text2)

            if hint_font is not None and death_count > 0:
                box_w = int(w * 0.7)
                box_h = 100
                left = cx - box_w // 2
                right = cx + box_w // 2
                bottom = restart_y + RESTART_FONT_SIZE + 10
                top = bottom + box_h
                phase = death_count % 4
                if phase == 1:
                    msg1 = '보스의 공격은 엇박자로 이루어집니다.'
                    msg2 = '구르기를 남발해도 계속 살 수 없습니다.'
                elif phase == 2:
                    msg1 = '보스의 순간이동 공격은 쿨타임이 존재합니다.'
                    msg2 = '또한 보스의 준비 자세를 잘 보세요'
                elif phase == 3:
                    msg1 = '라이프는 무한합니다.'
                    msg2 = '보스의 HP도 연속적입니다.'
                else:
                    msg1 = '보스를 공격해도 그의 공격은 끊기지 않습니다.'
                    msg2 = '타이밍을 잘 잡으세요.'

                text_x = left + 200
                center_y = bottom + 400
                hint_font.draw(text_x, center_y + 10, msg1, (255, 255, 255))
                hint_font.draw(text_x, center_y - 20, msg2, (255, 255, 255))

    update_canvas()
