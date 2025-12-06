from pico2d import *
import game_framework
from stage0 import hint_font

stage2_image = None
hint_font = None


def enter():
    global stage2_image, hint_font
    stage2_image = load_image('stage2.png')
    hint_font = load_font('neodgm.ttf', 20)



def exit():
    global stage2_image, hint_font
    stage2_image = None
    hint_font = None



def handle_events(events):
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()
            elif e.key == SDLK_q:
                game_framework.change_to_loading()
                return


def update(dt):
    pass

def draw():
    clear_canvas()
    if stage2_image is not None:
        w = get_canvas_width()
        h = get_canvas_height()
        iw, ih = stage2_image.w, stage2_image.h
        scale = min(w / iw, h / ih)
        dw = int(iw * scale)
        dh = int(ih * scale)
        stage2_image.draw(w // 2, h // 2, dw, dh)

    if hint_font is not None:
        w = get_canvas_width()
        h = get_canvas_height()
        hint_font.draw(10, h - 30, 'q : 로딩 화면 전환', (255, 255, 255))

    update_canvas()



def draw():
    clear_canvas()
    if stage2_image is not None:
        w = get_canvas_width()
        h = get_canvas_height()
        iw, ih = stage2_image.w, stage2_image.h
        scale = min(w / iw, h / ih)
        dw = int(iw * scale)
        dh = int(ih * scale)
        stage2_image.draw(w // 2, h // 2, dw, dh)
    update_canvas()
