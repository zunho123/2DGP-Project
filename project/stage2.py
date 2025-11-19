from pico2d import *
import game_framework

stage2_image = None


def enter():
    global stage2_image
    stage2_image = load_image('stage2.png')


def exit():
    global stage2_image
    stage2_image = None


def handle_events(events):
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()


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
    update_canvas()
