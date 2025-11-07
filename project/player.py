from pico2d import *

IDLE, RUN, JUMP, ATTACK = 0, 1, 2, 3

def _finalize(meta):
    pad = meta.get('pad', 0)
    eff = [max(1, w - 2 * pad) for w in meta['widths']]
    meta['aw'] = sum(eff) / len(eff)

class Player:
    RUN_SPEED_PPS = 260.0
    GRAVITY_PPS2 = -2000.0
    JUMP_VEL_PPS = 520.0

    def __init__(self, stage):
        self.stage = stage
        self.img_idle = load_image('idle.png')
        self.img_run = load_image('run.png')
        self.img_jump = load_image('jump.png')
        self.img_attack = load_image('attack.png')

        self.data_idle = dict(lefts=[8,45,84,123,162,202,242,282,321,360], widths=[31,31,32,32,33,33,33,32,32,31], pad=1)
        self.data_run  = dict(lefts=[11,55,98,141,184,227,271,314,359,405], widths=[39,38,38,38,38,39,38,40,41,41], pad=1)
        self.data_jump = dict(lefts=[11,45,80,115,168,214,260,306], widths=[29,30,30,29,41,41,41,41], pad=1)
        self.data_attack = dict(lefts=[12,57,111,158,207,254,303], widths=[38,47,40,42,40,42,42], pad=0)

        for d in (self.data_idle, self.data_run, self.data_jump, self.data_attack):
            _finalize(d)

        self.scale = 0.5
        self.x = self.stage.bg_w // 2
        self.ground_y = self.stage.ground_y
        self.ground_off = 0
        self.y = self.ground_y + self.ground_off
        self.vy = 0.0

        self.state = IDLE
        self.dir = 1
        self.frame = 0
        self.jump_frame = 0
        self.atk_frame = 0
        self.tacc = 0.0
        self.atk_tacc = 0.0

    def request_jump(self):
        if self.state != JUMP and self.state != ATTACK and abs(self.y - (self.ground_y + self.ground_off)) < 1e-3:
            self.state = JUMP
            self.vy = self.JUMP_VEL_PPS
            self.jump_frame = 0
            self.tacc = 0.0

    def request_attack(self):
        if self.state != JUMP and self.state != ATTACK:
            self.state = ATTACK
            self.atk_frame = 0
            self.atk_tacc = 0.0

    def _anim_step(self, dt, gap, maxf, attr):
        self.tacc += dt
        while self.tacc >= gap:
            v = getattr(self, attr)
            v = (v + 1) % maxf
            setattr(self, attr, v)
            self.tacc -= gap

    def update(self, dt, move_dir):
        if self.state not in (JUMP, ATTACK):
            if move_dir != 0:
                self.state = RUN
                self.dir = -1 if move_dir < 0 else 1
            else:
                self.state = IDLE

        speed = self.RUN_SPEED_PPS if self.state != IDLE else 0.0
        if self.state == JUMP and move_dir != 0:
            speed *= 0.7
            self.dir = -1 if move_dir < 0 else 1
        self.x += move_dir * speed * dt
        self.x = max(20, min(self.x, self.stage.bg_w - 20))

        self.vy += self.GRAVITY_PPS2 * dt
        self.y += self.vy * dt
        gy = self.ground_y + self.ground_off
        if self.y < gy:
            self.y = gy
            self.vy = 0.0
            if self.state == JUMP:
                self.state = RUN if move_dir != 0 else IDLE
                self.frame = 0
                self.tacc = 0.0

        if self.state == IDLE:
            self._anim_step(dt, 0.08, len(self.data_idle['widths']), 'frame')
        elif self.state == RUN:
            self._anim_step(dt, 0.04, len(self.data_run['widths']), 'frame')
        elif self.state == JUMP:
            self.tacc += dt
            gap = 0.06
            while self.tacc >= gap:
                self.jump_frame = min(self.jump_frame + 1, len(self.data_jump['widths']) - 1)
                self.tacc -= gap
        else:
            self.atk_tacc += dt
            while self.atk_tacc >= 0.045:
                self.atk_frame += 1
                self.atk_tacc -= 0.045
                if self.atk_frame >= len(self.data_attack['widths']):
                    self.state = RUN if move_dir != 0 else IDLE
                    self.frame = 0
                    self.tacc = 0.0
                    self.atk_frame = 0
                    break

    def _draw_strip(self, img, data, fi, stage, flip=False):
        pad = data.get('pad', 0)
        w_src = data['widths'][fi] - 2 * pad
        l_src = data['lefts'][fi] + pad
        h = img.h
        dw = int(w_src * self.scale * stage.window_w / stage.vw)
        dh = int(h * self.scale * stage.window_h / stage.vh)
        cx = (self.x + ((w_src - data['aw']) / 2)) - stage.left
        cy = (self.y) - stage.bottom
        sx = int(cx * stage.window_w / stage.vw)
        sy = int(cy * stage.window_h / stage.vh) + dh // 2
        if flip:
            img.clip_composite_draw(l_src, 0, w_src, h, 0, 'h', sx, sy, dw, dh)
        else:
            img.clip_draw(l_src, 0, w_src, h, sx, sy, dw, dh)

    def draw(self, stage):
        if self.state == IDLE:
            self._draw_strip(self.img_idle, self.data_idle, self.frame, stage, self.dir == -1)
        elif self.state == RUN:
            self._draw_strip(self.img_run, self.data_run, self.frame, stage, self.dir == -1)
        elif self.state == JUMP:
            self._draw_strip(self.img_jump, self.data_jump, self.jump_frame, stage, self.dir == -1)
        else:
            self._draw_strip(self.img_attack, self.data_attack, self.atk_frame, stage, self.dir == -1)
