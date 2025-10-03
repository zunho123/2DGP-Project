from pico2d import *

open_canvas(1280, 720)


img_run = load_image('run.png')
img_attack = load_image('attack.png')
img_jump_attack = load_image('jump_attack.png')
img_spin_attack = load_image('spin_attack.png')
img_damage = load_image('damage.png')

data_run = dict (
    lefts=[15, 112, 204, 291, 377, 472, 561, 648],
    widths=[84, 79, 74, 72, 81, 75, 73, 75]
)
data_attack = dict (
    lefts  =[16,81,179,310,403,488,572,657,772,886],
    widths =[64,89,122,85,82,63,73,107,105,90]
)
data_jump_attack = dict (
    lefts=[9, 82, 163, 244, 308, 381, 466, 518, 571, 623, 678, 733, 788, 839],
    widths =[62,70,68,53,63,62,43,43,43,45,46,45,42,63]
)
data_spin_attack = dict(
    lefts  =[14,99,196,288,385,488,578,641,740,832,923,1006,1120,1215,1311,1406,1501,1596],
    widths =[75,85,80,85,91,78,51,87,80,83,74,106,87,85,86,86,87,87]
)
data_damage = dict(
    lefts  =[16,115,201,288,392,561,664,763,843],
    widths =[79,67,84,91,152,90,90,79,76]
)

CenterX, CenterY = 640, 110
SCALE = 5.0
frame_gap = 0.06

def play_animation(img, data, CenterX, CenterY, repeat=5, frame_gap=0.06, SCALE=5.0):
    lefts = data['lefts']
    widths = data['widths']

    aw = sum(widths) / len(widths)
    h = img.h

    for _ in range(repeat):
        for l, w in zip(lefts, widths):
            dw = int(w * SCALE)
            dh = int(h * SCALE)
            x = CenterX
            y = int(CenterY + dh / 2)

            x_offset = int(((w- aw) / 2) * SCALE)
            x += x_offset

            clear_canvas()
            img.clip_composite_draw(l, 0, w, h, 0, '', x, y, dw, dh)
            update_canvas()
            delay(frame_gap)

try:
    actions = [
        (img_run,    data_run,    frame_gap),
        (img_attack, data_attack, frame_gap),
        (img_jump_attack, data_jump_attack, frame_gap),
        (img_spin_attack, data_spin_attack, frame_gap),
        (img_damage, data_damage, frame_gap + 0.03)
    ]
    while True:
        for img, meta, FG in actions:
            play_animation(img, meta, CenterX, CenterY, repeat=5, frame_gap = FG, SCALE=SCALE)
            delay(1.0)
except KeyboardInterrupt:
    pass
finally:
    close_canvas()