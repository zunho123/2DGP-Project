from pico2d import *

WINDOW_W, WINDOW_H = 1280, 720
CENTER_X, CENTER_Y = WINDOW_W // 2, 220
SCALE = 4.0

open_canvas(WINDOW_W, WINDOW_H)

img_idle       = load_image('idle.png')
img_cas_idle   = load_image('casual_idle.png')
img_run        = load_image('run.png')
img_cas_walk   = load_image('casual_walk.png')

data_idle = dict(
    lefts  =[8,45,84,123,162,202,242,282,321,360],
    widths =[31,31,32,32,33,33,33,32,32,31]
)
data_casual_idle = dict(
    lefts  =[12,45,78,111,144,178,213,248,283,319,353],
    widths =[26,26,26,26,27,28,28,28,28,26,26]
)
data_run = dict(
    lefts  =[11, 55, 98, 141, 184, 227, 271, 314, 359, 405],
    widths =[39, 38, 38, 38, 38, 39, 38, 40, 41, 41]
)
data_casual_walk = dict(
    lefts  =[11,46,80,116,153,186,220,254],
    widths =[28,28,29,30,26,27,27,28]
)

def play_center(img, data, loops=3, frame_gap=0.08, scale=SCALE):
    lefts, widths = data['lefts'], data['widths']
    h = img.h
    aw = sum(widths) / len(widths)
    for _ in range(loops):
        for l, w in zip(lefts, widths):
            dw, dh = int(w * scale), int(h * scale)
            x = CENTER_X + int(((w - aw) / 2) * scale)
            y = CENTER_Y + dh // 2
            clear_canvas()
            img.clip_draw(l, 0, w, h, x, y, dw, dh)
            update_canvas()
            delay(frame_gap)

def play_lr(img, data, step_px=14, frame_gap=0.05, scale=SCALE):
    lefts, widths = data['lefts'], data['widths']
    h = img.h
    aw = sum(widths) / len(widths)
    i = 0
    for x in range(-200, WINDOW_W + 200, step_px):
        w = widths[i]; l = lefts[i]
        dw, dh = int(w * scale), int(h * scale)
        xx = x + int(((w - aw) / 2) * scale)
        yy = CENTER_Y + dh // 2
        clear_canvas()
        img.clip_draw(l, 0, w, h, xx, yy, dw, dh)
        update_canvas()
        i = (i + 1) % len(widths)
        delay(frame_gap)

play_center(img_idle, data_idle, loops=3, frame_gap=0.08)
play_center(img_cas_idle, data_casual_idle, loops=3, frame_gap=0.08)
play_lr(img_run, data_run, step_px=16, frame_gap=0.04)
play_lr(img_cas_walk, data_casual_walk, step_px=10, frame_gap=0.055)

close_canvas()
