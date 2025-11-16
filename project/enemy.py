from pico2d import *

EN_IDLE, EN_DEAD = 0, 1

class Enemy:
    def __init__(self, stage, scale=1.0):
        self.stage = stage
        self.img_idle = load_image('enemy_idle.png')
        self.img_dead = load_image('enemy_dead.png')
        self.cols = 12
        self.data_dead = dict(
            lefts=[13, 48, 89, 132, 175, 218, 274, 325, 394, 459, 523, 588],
            widths=[32, 35, 41, 41, 41, 41, 40, 65, 57, 55, 56, 55],
            pad=1
        )
        pad = self.data_dead.get('pad', 0)
        eff = [max(1, w - 2 * pad) for w in self.data_dead['widths']]
        self.data_dead['aw'] = sum(eff) / len(eff)

        self.char_scale = scale
        self.x = min(stage.w - 20, stage.w // 2 + 140)
        self.ground_off = 5
        self.y = stage.ground_y + self.ground_off + 2
        self.dir = -1
        self.run_speed = 0.0
        self.gravity = -2000.0
        self.vy = 0.0
        self.on_ground = True

        self.state = EN_IDLE
        self.frame = 0
        self.tacc = 0.0
        self.gap = 0.08

        self.dead_frame = 0
        self.dead_tacc = 0.0
        self.dead_gap = 0.06

    def is_alive(self):
        return self.state == EN_IDLE

    def die(self):
        if self.state != EN_DEAD:
            self.state = EN_DEAD
            self.dead_frame = 0
            self.dead_tacc = 0.0
            self.vy = 0.0

    def is_dead(self):
        return self.state == EN_DEAD

    def aabb(self):
        fw = (self.img_idle.w // self.cols) * self.char_scale * 0.6
        fh = self.img_idle.h * self.char_scale * 0.8 + 5
        l = self.x - fw * 0.5
        r = self.x + fw * 0.5
        b = self.y + 8
        t = self.y + fh
        return l, b, r, t

    def get_bb(self):
        return self.aabb()

    def update(self, dt):
        self.stage.apply_physics(self, dt, 0)
        if self.state == EN_IDLE:
            self.tacc += dt
            while self.tacc >= self.gap:
                self.tacc -= self.gap
                self.frame = (self.frame + 1) % self.cols
        else:
            self.dead_tacc += dt
            while self.dead_tacc >= self.dead_gap:
                self.dead_tacc -= self.dead_gap
                if self.dead_frame < len(self.data_dead['widths']) - 1:
                    self.dead_frame += 1

    def draw(self):
        if self.state == EN_IDLE:
            self.stage.draw_strip(self.img_idle, self.cols, self.frame,
                                  self.x, self.y, self.char_scale, self.dir == -1, pad=0)
        else:
            self.stage.draw_frame(self.img_dead, self.data_dead, self.dead_frame,
                                  self.x, self.y, self.char_scale, False)
        l, b, r, t = self.get_bb()
        sx1, sy1 = self.stage.to_screen(l, b)
        sx2, sy2 = self.stage.to_screen(r, t)
        draw_rectangle(sx1, sy1, sx2, sy2)
