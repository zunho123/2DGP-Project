from pico2d import *


class KillSlashEffect:
    def __init__(self, stage, x, y, dir, scale=1.0, duration=0.25):
        self.stage = stage
        self.img = load_image('kill_slash.png')
        self.x = x
        self.y = y
        self.dir = dir
        self.scale = scale
        self.duration = duration
        self.t = 0.0

    def update(self, dt):
        self.t += dt

    def is_alive(self):
        return self.t < self.duration

    def draw(self):
        sx, sy = self.stage.to_screen(self.x, self.y)
        w = self.img.w * self.scale
        h = self.img.h * self.scale
        self.img.draw(sx, sy, w, h)
