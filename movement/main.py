from pico2d import *
import time

WINDOW_W, WINDOW_H = 1280, 720
CENTER_X, CENTER_Y = WINDOW_W // 2, 220
SCALE = 4.0
RUN_SPEED_PPS = 300.0

open_canvas(WINDOW_W, WINDOW_H)

img_idle     = load_image('idle.png')
img_run      = load_image('run.png')

data_idle = dict(
    lefts  =[8,45,84,123,162,202,242,282,321,360],
    widths =[31,31,32,32,33,33,33,32,32,31]
)
data_run = dict(
    lefts  =[11, 55, 98, 141, 184, 227, 271, 314, 359, 405],
    widths =[39, 38, 38, 38, 38, 39, 38, 40, 41, 41]
)

def prep(d):
    d['aw'] = sum(d['widths']) / len(d['widths'])
prep(data_idle); prep(data_run)

IDLE, RUN = 0, 1
state = IDLE
dir = 1
x = CENTER_X
frame = 0
tacc = 0.0
left_pressed = False
right_pressed = False
running = True
last = time.time()

def draw_frame(img, data, fi, x, y, scale, flip=False):
    w = data['widths'][fi]
    l = data['lefts'][fi]
    h = img.h
    dx = x + int(((w - data['aw']) / 2) * scale)
    dw, dh = int(w * scale), int(h * scale)
    if flip:
        img.clip_composite_draw(l, 0, w, h, 0, 'h', dx, y + dh // 2, dw, dh)
    else:
        img.clip_draw(l, 0, w, h, dx, y + dh // 2, dw, dh)

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
        x += dir * RUN_SPEED_PPS * dt
        x = max(40, min(WINDOW_W - 40, x))

    gap = 0.08 if state == IDLE else 0.04
    maxf = len(data_idle['widths']) if state == IDLE else len(data_run['widths'])
    tacc += dt
    while tacc >= gap:
        frame = (frame + 1) % maxf
        tacc -= gap

    clear_canvas()
    if state == IDLE:
        draw_frame(img_idle, data_idle, frame, x, CENTER_Y, SCALE, flip=(dir == -1))
    else:
        draw_frame(img_run, data_run, frame, x, CENTER_Y, SCALE, flip=(dir == -1))
    update_canvas()
    delay(0.001)

close_canvas()
