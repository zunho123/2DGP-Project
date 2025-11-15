from pico2d import *
import game_framework
import loading_mode

logo_image = None
elapsed = 0.0
LOGO_DURATION = 3.0

def enter():
    global logo_image, elapsed
    logo_image = load_image('Logo.png')
    elapsed = 0.0

def exit():
    global logo_image
    logo_image = None

def handle_events(events):
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_ESCAPE:
                game_framework.quit()

def update(dt):
    global elapsed
    elapsed += dt
    if elapsed >= LOGO_DURATION:
        game_framework.change_state(loading_mode)

def draw():
    clear_canvas()
    if logo_image is not None:
        w = get_canvas_width()
        h = get_canvas_height()
        logo_image.draw(w // 2, h // 2, w, h)
    update_canvas()
