from pico2d import *
from anim import SpriteAnim

ENEMY_IDLE, ENEMY_DEAD = 0, 1

class Enemy:
    def __init__(self, stage, x_init):
        self.stage = stage
        self.x = min(stage.bg_w - 20, x_init)
        self.y = stage.ground_y
        self.alive = True
        self.state = ENEMY_IDLE
        self.scale = 1.0
        self.idle_img = load_image('enemy_idle.png')
        self.idle_cols = 12
        self.idle_pad = 0
        self.idle_frame = 0
        self.idle_gap = 0.08
        self.idle_tacc = 0.0
        self.dead = SpriteAnim('enemy_dead.png', [13,48,89,132,175,218,274,325,394,459,523,588], [32,35,41,41,41,41,40,65,57,55,56,55], pad=1)
        self.dead.set_gap(0.06)
        self.foot = 6
        self.ground_off = 6

    def get_bb(self):
        fw = (self.idle_img.w // self.idle_cols) * self.scale * 0.6
        fh = self.idle_img.h * self.scale * 0.8
        l = self.x - fw * 0.5
        r = self.x + fw * 0.5
        b = self.y
        t = self.y + fh
        return l, b, r, t

    def kill(self):
        if self.alive:
            self.alive = False
            self.state = ENEMY_DEAD
            self.dead.reset()

    def update(self, dt):
        if self.state == ENEMY_IDLE:
            self.idle_tacc += dt
            while self.idle_tacc >= self.idle_gap:
                self.idle_frame = (self.idle_frame + 1) % self.idle_cols
                self.idle_tacc -= self.idle_gap
        else:
            self.dead.step(dt, loop=False)

    def draw(self):
        if self.state == ENEMY_IDLE:
            fh = self.idle_img.h
            fw = self.idle_img.w // self.idle_cols
            l_src = fw * (self.idle_frame % self.idle_cols)
            sx = self.stage.window_w / self.stage.vw
            sy = self.stage.window_h / self.stage.vh
            dw = int(fw * self.scale * sx)
            dh = int(fh * self.scale * sy)
            sxp, syp_base = self.stage.world_to_screen(self.x, self.y)
            syp = syp_base + dh // 2 - int(self.foot * self.scale * sy) - int(self.ground_off * self.scale * sy)
            self.idle_img.clip_draw(l_src, 0, fw, fh, sxp, syp, dw, dh)
        else:
            self.dead.draw_world(self.stage, self.x, self.y, self.scale, flip=False, foot_off_px=self.foot, ground_off_px=self.ground_off)
