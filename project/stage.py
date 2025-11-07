from pico2d import *

class Stage:
    def __init__(self, bg_path, window_w, window_h, zoom_mul=1.4, ground_ratio=0.0, ground_px=22, snap=6.0):
        self.window_w = window_w
        self.window_h = window_h
        self.bg = load_image(bg_path)
        self.bg_w, self.bg_h = self.bg.w, self.bg.h
        self.base_zoom = min(window_w / self.bg_w, window_h / self.bg_h)
        self.left = 0.0
        self.bottom = 0.0
        self.snap = snap
        self.set_zoom_mul(zoom_mul)
        self.ground_ratio = ground_ratio
        self.ground_px = ground_px
        self.ground_y = int(self.bg_h * self.ground_ratio) + self.ground_px

    def set_zoom_mul(self, k):
        self.zoom = max(0.1, self.base_zoom * k)
        self.vw = self.window_w / self.zoom
        self.vh = self.window_h / self.zoom

    def set_ground_px(self, px):
        self.ground_px = int(px)
        self.ground_y = int(self.bg_h * self.ground_ratio) + self.ground_px

    def clamp_left(self, left):
        return max(0.0, min(left, max(0.0, self.bg_w - self.vw)))

    def set_view_by_center(self, x, lead_px=0.0):
        center = x + lead_px
        left = center - self.vw / 2.0
        self.left = self.clamp_left(left)
        self.bottom = 0.0

    def set_view_follow(self, x, dt, lead_px=0.0):
        center = x + lead_px
        target_left = self.clamp_left(center - self.vw / 2.0)
        a = min(1.0, max(0.0, dt * self.snap))
        self.left += (target_left - self.left) * a
        self.bottom = 0.0

    def world_to_screen(self, x, y):
        sx = self.window_w / self.vw
        sy = self.window_h / self.vh
        return int((x - self.left) * sx), int((y - self.bottom) * sy)

    def draw(self):
        self.bg.clip_draw(int(self.left), int(self.bottom), int(self.vw), int(self.vh),
                          self.window_w // 2, self.window_h // 2, self.window_w, self.window_h)
