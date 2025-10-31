from pico2d import *

class Stage:
    def __init__(self, bg_path, window_w, window_h):
        self.window_w = window_w
        self.window_h = window_h
        self.bg = load_image(bg_path)
        self.bg_w = self.bg.w
        self.bg_h = self.bg.h
        self.zoom = max(self.window_w / self.bg_w, self.window_h / self.bg_h)
        self.left = 0
        self.bottom = 0
        self.vw = self.window_w / self.zoom
        self.vh = self.window_h / self.zoom
        self.ground_ratio = 0.0
        self.ground_y = int(self.bg_h * self.ground_ratio)

    def set_view_by_center(self, x_center):
        self.vw = self.window_w / self.zoom
        self.vh = self.window_h / self.zoom
        self.left = max(0, min(x_center - self.vw / 2, max(0, self.bg_w - self.vw)))
        self.bottom = 0

    def world_to_screen(self, x, y):
        sx = self.window_w / self.vw
        sy = self.window_h / self.vh
        return int((x - self.left) * sx), int((y - self.bottom) * sy)

    def draw(self):
        self.bg.clip_draw(int(self.left), int(self.bottom), int(self.vw), int(self.vh), self.window_w // 2, self.window_h // 2, self.window_w, self.window_h)
