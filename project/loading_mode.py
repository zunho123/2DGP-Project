from pico2d import *
import game_framework
import play_mode
import stage0

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

                left0 = int(w * 0.6)
                right0 = int(w * 1.0)
                bottom0 = int(h * 0.60)
                top0 = int(h * 0.80)
                if left0 <= mx <= right0 and bottom0 <= my <= top0:
                    game_framework.change_state(stage0)
                    return

                left1 = int(w * 0.6)
                right1 = int(w * 1.0)
                bottom1 = int(h * 0.30)
                top1 = int(h * 0.50)
                if left1 <= mx <= right1 and bottom1 <= my <= top1:
                    game_framework.change_state(play_mode)


def update(dt):
    pass


def draw():
    clear_canvas()
    if loading_image is not None:
        w = get_canvas_width()
        h = get_canvas_height()
        loading_image.draw(w // 2, h // 2, w, h)

        left0 = int(w * 0.6)
        right0 = int(w * 1.0)
        bottom0 = int(h * 0.60)
        top0 = int(h * 0.80)
        draw_rectangle(left0, bottom0, right0, top0)

        left1 = int(w * 0.6)
        right1 = int(w * 1.0)
        bottom1 = int(h * 0.30)
        top1 = int(h * 0.50)
        draw_rectangle(left1, bottom1, right1, top1)

    update_canvas()
