from pico2d import *

SN_IDLE, SN_ATTACK, SN_DEAD = 0, 1, 2


class Snow:
    def __init__(self, stage, x=900, scale=1.0):
        self.stage = stage
        self.img_idle = load_image('snow_idle.png')
        self.img_dead = load_image('snow_dead.png')
        self.img_attack = load_image('snow_att.png')

        self.data_idle = dict(
            lefts=[6, 50, 92, 136, 179, 223, 266, 311, 355, 400, 443, 487, 530, 574],
            widths=[36, 35, 37, 36, 37, 37, 37, 36, 35, 34, 34, 34, 34, 34],
            pad=1
        )

        self.data_dead = dict(
            lefts=[0, 48, 96, 144, 192],
            widths=[48, 48, 48, 48, 48],
            pad=0
        )

        self.data_attack = dict(
            lefts=[9, 84, 200, 313, 427, 528, 619, 701, 784, 872, 959, 1042, 1132, 1216],
            widths=[56, 97, 99, 99, 88, 83, 79, 79, 80, 76, 75, 76, 75, 76],
            pad=1
        )

        for d in (self.data_idle, self.data_dead, self.data_attack):
            pad = d.get('pad', 0)
            eff = [max(1, w - 2 * pad) for w in d['widths']]
            d['aw'] = sum(eff) / len(eff)

        self.char_scale = scale
        self.x = x
        self.ground_off = 0
        self.y_idle = stage.ground_y + self.ground_off + 17.5
        self.y_attack = stage.ground_y + self.ground_off + 10
        self.y = self.y_idle

        self.state = SN_IDLE

        self.frame = 0
        self.tacc = 0.0
        self.idle_gap = 0.08

        self.attack_frame = 0
        self.attack_tacc = 0.0
        self.attack_gap = 0.06

        self.dead_frame = 0
        self.dead_tacc = 0.0
        self.dead_gap = 0.08

        self.visible = True

    def start_attack(self, px, pdir):
        self.visible = True
        self.state = SN_ATTACK
        self.attack_frame = 0
        self.attack_tacc = 0.0
        offset = 70.0 * self.char_scale
        self.x = px + pdir * offset
        self.y = self.stage.ground_y + self.ground_off + 10.0

    def die(self):
        if self.state == SN_DEAD:
            return
        self.state = SN_DEAD
        self.dead_frame = 0
        self.dead_tacc = 0.0
        self.visible = True

    def update(self, dt):
        if self.state == SN_IDLE:
            self.tacc += dt
            while self.tacc >= self.idle_gap:
                self.tacc -= self.idle_gap
                self.frame = (self.frame + 1) % len(self.data_idle['widths'])

        elif self.state == SN_ATTACK:
            self.attack_tacc += dt
            while self.attack_tacc >= self.attack_gap:
                self.attack_tacc -= self.attack_gap
                if self.attack_frame < len(self.data_attack['widths']) - 1:
                    self.attack_frame += 1
                else:
                    self.state = SN_IDLE
                    self.attack_frame = 0
                    self.attack_tacc = 0.0
                    self.frame = 0
                    self.y = self.stage.ground_y + self.ground_off + 17.5
                    self.x -= 12.5
                    break

        elif self.state == SN_DEAD:
            if not self.visible:
                return
            self.dead_tacc += dt
            while self.dead_tacc >= self.dead_gap:
                self.dead_tacc -= self.dead_gap
                if self.dead_frame < len(self.data_dead['widths']) - 1:
                    self.dead_frame += 1
                else:
                    self.visible = False
                    break

    def get_bb(self):
        w = 30.0 * self.char_scale
        h = 40.0 * self.char_scale
        l = self.x - w * 0.5
        r = self.x + w * 0.5
        b = self.y
        t = self.y + h
        return l, b, r, t

    def is_dead(self):
        return self.state == SN_DEAD

    def draw(self):
        if not self.visible:
            return

        flip_flag = False

        if self.state == SN_IDLE:
            self.stage.draw_frame(
                self.img_idle, self.data_idle, self.frame,
                self.x, self.y, self.char_scale, flip_flag
            )
        elif self.state == SN_ATTACK:
            self.stage.draw_frame(
                self.img_attack, self.data_attack, self.attack_frame,
                self.x, self.y, self.char_scale, flip_flag
            )
        else:
            self.stage.draw_frame(
                self.img_dead, self.data_dead, self.dead_frame,
                self.x, self.y, self.char_scale, flip_flag
            )
