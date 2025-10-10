from pico2d import *
import time

WINDOW_W, WINDOW_H = 1280, 720
RUN_SPEED_PPS = 260.0
ZOOM = 1.6
CHAR_SCALE = 1.2
GRAVITY_PPS2 = -2000.0
GROUND_RATIO = 0.07

open_canvas(WINDOW_W, WINDOW_H)

bg = load_image('ClubNeon1.png')
img_idle = load_image('idle.png')
img_run  = load_image('run.png')

data_idle = dict(
    lefts  =[8,45,84,123,162,202,242,282,321,360],
    widths =[31,31,32,32,33,33,33,32,32,31]
)
data_run = dict(
    lefts  =[11,55,98,141,184,227,271,314,359,405],
    widths =[39,38,38,38,38,39,38,40,41,41]
)
data_idle['aw'] = sum(data_idle['widths']) / len(data_idle['widths'])
data_run['aw']  = sum(data_run['widths'])  / len(data_run['widths'])

bg_w, bg_h = bg.w, bg.h
ground_y = int(bg_h * GROUND_RATIO)

IDLE, RUN = 0, 1
state = IDLE
dir = 1
xw = bg_w // 2
yw = ground_y
vy = 0.0
frame = 0
tacc = 0.0
left_pressed = False
right_pressed = False
running = True
last = time.time()

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def camera_view(x_center, zoom):
    vw = WINDOW_W / zoom
    vh = WINDOW_H / zoom
    left = clamp(x_center - vw / 2, 0, max(0, bg_w - vw))
    bottom = 0
    return left, bottom, vw, vh

def draw_world_bg(left, bottom, vw, vh):
    bg.clip_draw(int(left), int(bottom), int(vw), int(vh), WINDOW_W // 2, WINDOW_H // 2, WINDOW_W, WINDOW_H)

def draw_world_sprite(img, data, fi, x, y, flip, left, bottom, vw, vh):
    sx = WINDOW_W / vw
    sy = WINDOW_H / vh
    w = data['widths'][fi]
    l = data['lefts'][fi]
    h = img.h
    dw = int(w * CHAR_SCALE * sx)
    dh = int(h * CHAR_SCALE * sy)
    cx = (x + ((w - data['aw']) / 2)) - left
    cy = (y) - bottom
    sxp = int(cx * sx)
    syp = int(cy * sy) + dh // 2
    if flip:
        img.clip_composite_draw(l, 0, w, h, 0, 'h', sxp, syp, dw, dh)
    else:
        img.clip_draw(l, 0, w, h, sxp, syp, dw, dh)

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
        elif e.type == SDL_KEYUP:
            if e.key == SDLK_LEFT:
                left_pressed = False
            elif e.key == SDLK_RIGHT:
                right_pressed = False

    if left_pressed ^ right_pressed:
        state = RUN
        dir = -1 if left_pressed else 1
    else:
        state = IDLE

    if state == RUN:
        xw += dir * RUN_SPEED_PPS * dt
        xw = clamp(xw, 20, bg_w - 20)

    vy += GRAVITY_PPS2 * dt
    yw += vy * dt
    if yw < ground_y:
        yw = ground_y
        vy = 0.0

    gap = 0.08 if state == IDLE else 0.04
    maxf = len(data_idle['widths']) if state == IDLE else len(data_run['widths'])
    tacc += dt
    while tacc >= gap:
        frame = (frame + 1) % maxf
        tacc -= gap

    left, bottom, vw, vh = camera_view(xw, ZOOM)

    clear_canvas()
    draw_world_bg(left, bottom, vw, vh)
    if state == IDLE:
        draw_world_sprite(img_idle, data_idle, frame, xw, yw, (dir == -1), left, bottom, vw, vh)
    else:
        draw_world_sprite(img_run, data_run, frame, xw, yw, (dir == -1), left, bottom, vw, vh)
    update_canvas()
    delay(0.001)

close_canvas()
