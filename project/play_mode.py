from pico2d import *
import game_framework
import stage1_mode
from stage import Stage
from player import Player
from enemy import Enemy
from kill_effect import KillSlashEffect

stage = None
player = None
enemy = None
move_dir = 0
up_hint = None
can_enter_next = False
bgm = None
effects = []

TRIGGER_X_MAX = 120
PROMPT_SIZE = 56
PLAYER_SCALE_STAGE1 = 1.0


def rect_overlap(l1, b1, r1, t1, l2, b2, r2, t2):
    return not (r1 < l2 or r2 < l1 or t1 < b2 or t2 < b1)


def enter():
    global stage, player, enemy, up_hint, move_dir, can_enter_next, bgm, effects
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


def exit():
    global bgm
    if bgm is not None:
        bgm.stop()
    bgm = None


def handle_events(events):
    global move_dir, can_enter_next
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
    global can_enter_next, effects
    player.update(dt, move_dir)

    if enemy:
        if hasattr(enemy, 'is_alive') and enemy.is_alive():
            if hasattr(player, 'is_attacking_active') and player.is_attacking_active():
                l1, b1, r1, t1 = player.attack_hitbox()
                l2, b2, r2, t2 = enemy.aabb()
                if rect_overlap(l1, b1, r1, t1, l2, b2, r2, t2):
                    enemy.die()
                    ex = (l2 + r2) * 0.5
                    ey = (b2 + t2) * 0.5
                    dir = player.dir if hasattr(player, 'dir') else 1
                    effects.append(KillSlashEffect(stage, ex, ey, dir, scale=1.0))
        enemy.update(dt)

    for eff in effects:
        eff.update(dt)
    effects = [e for e in effects if e.is_alive()]

    stage.update(dt, player.x)
    near_stairs = (player.x <= TRIGGER_X_MAX) and abs(player.y - stage.ground_y) < 8
    can_enter_next = _enemy_dead() and near_stairs


def draw():
    clear_canvas()
    stage.draw()
    if enemy:
        enemy.draw()
    for eff in effects:
        eff.draw()
    player.draw()
    if can_enter_next and up_hint is not None:
        sx, sy = stage.to_screen(player.x, player.y)
        up_hint.draw(sx, sy + int(80 * stage.zoom), PROMPT_SIZE, PROMPT_SIZE)
    update_canvas()
