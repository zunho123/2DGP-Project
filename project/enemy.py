from pico2d import *

ENEMY_IDLE, ENEMY_DEAD = 0, 1

def _finalize(meta):
    pad = meta.get('pad', 0)
    eff = [max(1, w - 2 * pad) for w in meta['widths']]
    meta['aw'] = sum(eff) / len(eff)

class Enemy:
    def __init__(self, stage, x_init):
        self.stage = stage
        self.img_idle = load_image('enemy_idle.png')
        self.img_dead = load_image('enemy_dead.png')

        self.cols = 12
        self.pad_strip = 0

        self.data_dead = dict(
            lefts=[13,48,89,132,175,218,274,325,394,459,523,588],
            widths=[32,35,41,41,41,41,40,65,57,55,56,55],
            pad=1
        )
        _finalize(self.data_dead)

        self.scale = 0.5
        self.x = x_init
        self.ground_y = self.stage.ground_y
        self.ground_off = -10
        self.y = self.ground_y + self.ground_off

        self.dir = -1
        self.state = ENEMY_IDLE
        self.frame = 0
        self.dead_frame = 0
        self.tacc = 0.0
        self.dead_tacc = 0.0

    def die(self):
        if self.state != ENEMY_DEAD:
            self.state = ENEMY_DEAD
            self.dead_frame = 0
            self.dead_tacc = 0.0

    def update(self, dt, move_dir):
        self.y = self.ground_y + self.ground_off
        if self.state == ENEMY_IDLE:
            self.tacc += dt
            while self.tacc >= 0.08:
                self.frame = (self.frame + 1) % self.cols
                self.tacc -= 0.08
        else:
            self.dead_tacc += dt
            while self.dead_tacc >= 0.06:
                if self.dead_frame < len(self.data_dead['widths']) - 1:
                    self.dead_frame += 1
                self.dead_tacc -= 0.06

    def _draw_strip(self, img, cols, fi, stage, flip=False, pad=0):
        fh = img.h
        if pad > 0:
            fw = (img.w - pad * (cols + 1)) // cols
            l_src = pad + (fw + pad) * (fi % cols)
            w_src = fw
        else:
            fw = img.w // cols
            l_src = fw * (fi % cols)
            w_src = fw
        dw = int(w_src * self.scale * stage.window_w / stage.vw)
        dh = int(fh * self.scale * stage.window_h / stage.vh)
        cx = self.x - stage.left
        cy = self.y - stage.bottom
        sx = int(cx * stage.window_w / stage.vw)
        sy = int(cy * stage.window_h / stage.vh) + dh // 2
        if flip:
            img.clip_composite_draw(l_src, 0, w_src, fh, 0, 'h', sx, sy, dw, dh)
        else:
            img.clip_draw(l_src, 0, w_src, fh, sx, sy, dw, dh)

    def _draw_dead(self, img, data, fi, stage, flip=False):
        pad = data.get('pad', 0)
        w_src = data['widths'][fi] - 2 * pad
        l_src = data['lefts'][fi] + pad
        h = img.h
        dw = int(w_src * self.scale * stage.window_w / stage.vw)
        dh = int(h * self.scale * stage.window_h / stage.vh)
        cx = self.x - stage.left
        cy = self.y - stage.bottom
        sx = int(cx * stage.window_w / stage.vw)
        sy = int(cy * stage.window_h / stage.vh) + dh // 2
        if flip:
            img.clip_composite_draw(l_src, 0, w_src, h, 0, 'h', sx, sy, dw, dh)
        else:
            img.clip_draw(l_src, 0, w_src, h, sx, sy, dw, dh)

    def draw(self, stage):
        if self.state == ENEMY_IDLE:
            self._draw_strip(self.img_idle, self.cols, self.frame, stage, self.dir == -1, self.pad_strip)
        else:
            self._draw_dead(self.img_dead, self.data_dead, self.dead_frame, stage, self.dir == -1)
