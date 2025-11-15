from pico2d import *
import game_framework
import play_mode

loading_image = None
bgm = None

def enter():
    global loading_image, bgm
    loading_image = load_image('Loading.png')
    bgm = load_music('song_load.ogg')
    bgm.set_volume(64)
    bgm.repeat_play()

def exit():
    global loading_image, bgm
    if bgm is not None:
        bgm.stop()
    loading_image = None
    bgm = None

def handle_events(events):
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()
        elif e.type == SDL_MOUSEBUTTONDOWN:
            if e.button == SDL_BUTTON_LEFT:
                w = get_canvas_width()
                h = get_canvas_height()
                mx = e.x
                my = h - e.y - 1
                left = int(w * 0.7)
                right = int(w * 0.95)
                bottom = int(h * 0.45)
                top = int(h * 0.55)
                if left <= mx <= right and bottom <= my <= top:
                    game_framework.change_state(play_mode)

def update(dt):
    pass

def draw():
    clear_canvas()
    if loading_image is not None:
        w = get_canvas_width()
        h = get_canvas_height()
        loading_image.draw(w // 2, h // 2, w, h)
    update_canvas()
