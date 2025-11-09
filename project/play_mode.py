from pico2d import *
import game_framework
import stage1_mode
from stage import Stage
from player import Player
from enemy import Enemy

stage = None
player = None
enemy = None
move_dir = 0
up_hint = None
can_enter_next = False

TRIGGER_X_MAX = 120
PROMPT_SIZE = 56

def enter():
    global stage, player, enemy, up_hint, move_dir, can_enter_next
    stage = Stage('stage1.png', window_w=1280, window_h=720, zoom=4.0, ground_px=15)
    player = Player(stage)
    enemy = Enemy(stage)
    up_hint = load_image('upkey.png')
    move_dir = 0
    can_enter_next = False

def exit():
    pass

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
    if hasattr(enemy, 'is_dead') and callable(enemy.is_dead):
        return enemy.is_dead()
    return getattr(enemy, 'dead', False)

def update(dt):
    global can_enter_next
    player.update(dt, move_dir)
    if enemy:
        enemy.update(dt)
    stage.update(dt, player.x)
    near_stairs = (player.x <= TRIGGER_X_MAX) and abs(player.y - stage.ground_y) < 8
    can_enter_next = _enemy_dead() and near_stairs

def draw():
    clear_canvas()
    stage.draw()
    if enemy:
        enemy.draw()
    player.draw()
    if can_enter_next and up_hint is not None:
        sx, sy = stage.to_screen(player.x, player.y)
        up_hint.draw(sx, sy + int(80 * stage.zoom), PROMPT_SIZE, PROMPT_SIZE)
    update_canvas()
