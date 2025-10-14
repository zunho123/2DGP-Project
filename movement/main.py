from pico2d import *
import time

WINDOW_W, WINDOW_H = 1280, 720
RUN_SPEED_PPS = 260.0
ZOOM = 1.6
CHAR_SCALE = 1.0
GRAVITY_PPS2 = -2000.0
JUMP_VEL_PPS = 520.0
GROUND_RATIO = 0.07

open_canvas(WINDOW_W, WINDOW_H)

bg = load_image('ClubNeon1.png')
img_idle = load_image('idle.png')
img_run  = load_image('run.png')
img_jump = load_image('jump.png')
img_enemy_idle = load_image('enemy_idle.png')

data_idle = dict(
    lefts  =[8,45,84,123,162,202,242,282,321,360],
    widths =[31,31,32,32,33,33,33,32,32,31],
    pad=1
)
data_run = dict(
    lefts  =[11,55,98,141,184,227,271,314,359,405],
    widths =[39,38,38,38,38,39,38,40,41,41],
    pad=1
)
data_jump = dict(
    lefts  =[11,45,80,115,168,214,260,306],
    widths =[29,30,30,29,41,41,41,41],
    pad=1
)

def finalize(meta):
    pad = meta.get('pad', 0)
    eff = [max(1, w - 2 * pad) for w in meta['widths']]
    meta['aw'] = sum(eff) / len(eff)
finalize(data_idle); finalize(data_run); finalize(data_jump)

bg_w, bg_h = bg.w, bg.h
ground_y = int(bg_h * GROUND_RATIO)

IDLE, RUN, JUMP = 0, 1, 2
state = IDLE
dir = 1
xw = bg_w // 2
yw = ground_y
vy = 0.0
frame = 0
jump_frame = 0
tacc = 0.0
left_pressed = False
right_pressed = False
running = True
last = time.time()

enemy_cols = 12
enemy_xw = bg_w // 2
enemy_yw = ground_y
enemy_frame = 0
enemy_tacc = 0.0

def clampv(v, lo, hi):
    return max(lo, min(hi, v))

def camera_view(x_center, zoom):
    vw = WINDOW_W / zoom
    vh = WINDOW_H / zoom
    left = clampv(x_center - vw / 2, 0, max(0, bg_w - vw))
    return left, 0, vw, vh

def draw_world_bg(left, bottom, vw, vh):
    bg.clip_draw(int(left), int(bottom), int(vw), int(vh), WINDOW_W // 2, WINDOW_H // 2, WINDOW_W, WINDOW_H)

def draw_world_sprite(img, data, fi, x, y, flip, left, bottom, vw, vh):
    sx = WINDOW_W / vw
    sy = WINDOW_H / vh
    pad = data.get('pad', 0)
    w_src = data['widths'][fi] - 2 * pad
    l_src = data['lefts'][fi] + pad
    h = img.h
    dw = int(w_src * CHAR_SCALE * sx)
    dh = int(h * CHAR_SCALE * sy)
    cx = (x + ((w_src - data['aw']) / 2)) - left
    cy = (y) - bottom
    sxp = int(cx * sx)
    syp = int(cy * sy) + dh // 2
    if flip:
        img.clip_composite_draw(l_src, 0, w_src, h, 0, 'h', sxp, syp, dw, dh)
    else:
        img.clip_draw(l_src, 0, w_src, h, sxp, syp, dw, dh)

def draw_world_strip(img, cols, fi, x, y, flip, left, bottom, vw, vh):
    sx = WINDOW_W / vw
    sy = WINDOW_H / vh
    fw = img.w // cols
    fh = img.h
    dw = int(fw * CHAR_SCALE * sx)
    dh = int(fh * CHAR_SCALE * sy)
    cx = x - left
    cy = y - bottom
    sxp = int(cx * sx)
    syp = int(cy * sy) + dh // 2
    l_src = fw * (fi % cols)
    if flip:
        img.clip_composite_draw(l_src, 0, fw, fh, 0, 'h', sxp, syp, dw, dh)
    else:
        img.clip_draw(l_src, 0, fw, fh, sxp, syp, dw, dh)

while running:
    now = time.time()
    dt = now - last
    last = now

    for e in get_events():
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
                if state != JUMP and abs(yw - ground_y) < 1e-3:
                    state = JUMP
                    vy = JUMP_VEL_PPS
                    jump_frame = 0
                    tacc = 0.0
        elif e.type == SDL_KEYUP:
            if e.key == SDLK_LEFT:
                left_pressed = False
            elif e.key == SDLK_RIGHT:
                right_pressed = False

    if state != JUMP:
        if left_pressed ^ right_pressed:
            state = RUN
            dir = -1 if left_pressed else 1
        else:
            state = IDLE

    move_dir = (-1 if left_pressed else 0) + (1 if right_pressed else 0)
    speed = RUN_SPEED_PPS if state != IDLE else 0.0
    if state == JUMP and move_dir != 0:
        speed *= 0.7
        dir = -1 if move_dir < 0 else 1
    xw += move_dir * speed * dt
    xw = clampv(xw, 20, bg_w - 20)

    vy += GRAVITY_PPS2 * dt
    yw += vy * dt
    if yw < ground_y:
        yw = ground_y
        vy = 0.0
        if state == JUMP:
            state = RUN if move_dir != 0 else IDLE
            frame = 0
            tacc = 0.0

    left, bottom, vw, vh = camera_view(xw, ZOOM)

    if state == IDLE:
        gap = 0.08
        maxf = len(data_idle['widths'])
        tacc += dt
        while tacc >= gap:
            frame = (frame + 1) % maxf
            tacc -= gap
    elif state == RUN:
        gap = 0.04
        maxf = len(data_run['widths'])
        tacc += dt
        while tacc >= gap:
            frame = (frame + 1) % maxf
            tacc -= gap
    else:
        gap = 0.06
        maxf = len(data_jump['widths'])
        tacc += dt
        while tacc >= gap:
            jump_frame = min(jump_frame + 1, maxf - 1)
            tacc -= gap

    enemy_gap = 0.08
    enemy_tacc += dt
    while enemy_tacc >= enemy_gap:
        enemy_frame = (enemy_frame + 1) % enemy_cols
        enemy_tacc -= enemy_gap

    clear_canvas()
    draw_world_bg(left, bottom, vw, vh)
    draw_world_strip(img_enemy_idle, enemy_cols, enemy_frame, enemy_xw, enemy_yw, False, left, bottom, vw, vh)
    if state == IDLE:
        draw_world_sprite(img_idle, data_idle, frame, xw, yw, (dir == -1), left, bottom, vw, vh)
    elif state == RUN:
        draw_world_sprite(img_run, data_run, frame, xw, yw, (dir == -1), left, bottom, vw, vh)
    else:
        draw_world_sprite(img_jump, data_jump, jump_frame, xw, yw, (dir == -1), left, bottom, vw, vh)
    update_canvas()
    delay(0.001)

close_canvas()
