from pico2d import *

class Enemy:
    def __init__(self, stage, scale=0.9):
        self.stage = stage
        self.img_idle = load_image('enemy_idle.png')
        self.cols = 12
        self.frame = 0
        self.tacc = 0.0
        self.gap = 0.08
        self.char_scale = scale
        self.x = min(stage.w - 20, stage.w // 2 + 140)
        self.ground_off = -10
        self.y = stage.ground_y + self.ground_off + 2
        self.dir = -1
        self.run_speed = 0.0
        self.gravity = -2000.0
        self.vy = 0.0
        self.on_ground = True

    def update(self, dt):
        self.stage.apply_physics(self, dt, 0)
        self.tacc += dt
        if self.tacc >= self.gap:
            self.tacc -= self.gap
            self.frame = (self.frame + 1) % self.cols

    def draw(self):
        self.stage.draw_strip(self.img_idle, self.cols, self.frame, self.x, self.y, self.char_scale, self.dir == -1, pad=0)
