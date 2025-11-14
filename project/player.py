from pico2d import *

IDLE, RUN, JUMP, ATTACK = 0, 1, 2, 3

class Player:
    def __init__(self, stage, scale=1.0):
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
            pad = d.get('pad', 0)
            eff = [max(1, w - 2 * pad) for w in d['widths']]
            d['aw'] = sum(eff) / len(eff)

        self.char_scale = scale
        self.x = self.stage.w // 2
        self.ground_off = 0
        self.y = self.stage.ground_y + self.ground_off + 2
        self.dir = 1
        self.state = IDLE
        self.frame = 0
        self.jump_frame = 0
        self.atk_frame = 0
        self.tacc = 0.0
        self.atk_tacc = 0.0
        self.run_speed = 260.0
        self.gravity = -2000.0
        self.jump_vel = 520.0
        self.vy = 0.0
        self.on_ground = True

    def request_jump(self):
        if self.on_ground and self.state != ATTACK:
            self.state = JUMP
            self.vy = self.jump_vel
            self.jump_frame = 0
            self.tacc = 0.0

    def request_attack(self):
        if self.state != ATTACK:
            self.state = ATTACK
            self.atk_frame = 0
            self.atk_tacc = 0.0

    def is_attacking_active(self):
        return self.state == ATTACK and 2 <= self.atk_frame <= 5

    def attack_hitbox(self):
        fw = 70 * self.char_scale
        fh = 40 * self.char_scale
        off = 20 * self.char_scale
        if self.dir == 1:
            l = self.x + off
            r = self.x + off + fw
        else:
            l = self.x - off - fw
            r = self.x - off
        b = self.y + 20 * self.char_scale
        t = b + fh
        return l, b, r, t

    def update(self, dt, move_dir=0):
        if move_dir != 0:
            self.dir = 1 if move_dir > 0 else -1

        if self.state != JUMP and self.state != ATTACK:
            if move_dir != 0:
                self.state = RUN
            else:
                self.state = IDLE

        self.stage.apply_physics(self, dt, move_dir)

        if self.state == IDLE:
            self.tacc += dt
            while self.tacc >= 0.08:
                self.tacc -= 0.08
                self.frame = (self.frame + 1) % len(self.data_idle['widths'])
        elif self.state == RUN:
            self.tacc += dt
            while self.tacc >= 0.04:
                self.tacc -= 0.04
                self.frame = (self.frame + 1) % len(self.data_run['widths'])
        elif self.state == JUMP:
            self.tacc += dt
            while self.tacc >= 0.06:
                self.tacc -= 0.06
                self.jump_frame = min(self.jump_frame + 1, len(self.data_jump['widths']) - 1)
            if self.on_ground:
                self.state = RUN if move_dir != 0 else IDLE
                self.frame = 0
                self.tacc = 0.0
        else:
            self.atk_tacc += dt
            while self.atk_tacc >= 0.045:
                self.atk_tacc -= 0.045
                self.atk_frame += 1
                if self.atk_frame >= len(self.data_attack['widths']):
                    if self.on_ground:
                        self.state = RUN if move_dir != 0 else IDLE
                        self.frame = 0
                        self.tacc = 0.0
                    else:
                        self.state = JUMP
                    self.atk_frame = 0
                    break

    def draw(self):
        flip = (self.dir == -1)
        if self.state == IDLE:
            self.stage.draw_frame(self.img_idle, self.data_idle, self.frame, self.x, self.y, self.char_scale, flip)
        elif self.state == RUN:
            self.stage.draw_frame(self.img_run, self.data_run, self.frame, self.x, self.y, self.char_scale, flip)
        elif self.state == JUMP:
            self.stage.draw_frame(self.img_jump, self.data_jump, self.jump_frame, self.x, self.y, self.char_scale, flip)
        else:
            self.stage.draw_frame(self.img_attack, self.data_attack, self.atk_frame, self.x, self.y, self.char_scale, flip)
