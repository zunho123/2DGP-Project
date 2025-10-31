from anim import SpriteAnim

IDLE, RUN, JUMP, ATTACK = 0, 1, 2, 3

class Player:
    def __init__(self, stage):
        self.stage = stage
        self.x = stage.bg_w // 2
        self.y = stage.ground_y
        self.vy = 0.0
        self.dir = 1
        self.state = IDLE
        self.scale = 1.0
        self.run_speed_pps = 260.0
        self.gravity_pps2 = -2000.0
        self.jump_vel_pps = 520.0
        self.ax = 0
        self.idle = SpriteAnim('idle.png', [8,45,84,123,162,202,242,282,321,360], [31,31,32,32,33,33,33,32,32,31], pad=1)
        self.run = SpriteAnim('run.png', [11,55,98,141,184,227,271,314,359,405], [39,38,38,38,38,39,38,40,41,41], pad=1)
        self.jump = SpriteAnim('jump.png', [11,45,80,115,168,214,260,306], [29,30,30,29,41,41,41,41], pad=1)
        self.attack = SpriteAnim('attack.png', [12,57,111,158,207,254,303], [38,47,40,42,40,42,42], pad=0)
        self.idle.set_gap(0.08)
        self.run.set_gap(0.04)
        self.jump.set_gap(0.06)
        self.attack.set_gap(0.045)
        self.foot_idle = 2
        self.foot_run = 2
        self.foot_jump = 4
        self.foot_attack = 2
        self.ground_off = 12

    def input_axis(self, l, r):
        self.ax = (-1 if l else 0) + (1 if r else 0)

    def request_jump(self):
        if self.state != JUMP and abs(self.y - self.stage.ground_y) < 1e-3 and self.state != ATTACK:
            self.state = JUMP
            self.vy = self.jump_vel_pps
            self.jump.reset()

    def request_attack(self):
        if self.state != JUMP and self.state != ATTACK:
            self.state = ATTACK
            self.attack.reset()

    def attack_active(self):
        return self.state == ATTACK and 2 <= self.attack.frame <= 5

    def attack_hit(self, bb):
        l1, b1, r1, t1 = self.get_attack_rect()
        l2, b2, r2, t2 = bb
        return not (r1 < l2 or r2 < l1 or t1 < b2 or t2 < b1)

    def get_attack_rect(self):
        fw = 70 * self.scale
        fh = 40 * self.scale
        off = 20 * self.scale
        if self.dir == 1:
            l = self.x + off
            r = self.x + off + fw
        else:
            l = self.x - off - fw
            r = self.x - off
        b = self.y + 20 * self.scale
        t = b + fh
        return l, b, r, t

    def update(self, dt):
        if self.state not in (JUMP, ATTACK):
            if self.ax != 0:
                self.state = RUN
                self.dir = -1 if self.ax < 0 else 1
            else:
                self.state = IDLE
        move_dir = self.ax
        if self.state == ATTACK:
            move_dir = 0
        speed = self.run_speed_pps if self.state != IDLE else 0.0
        if self.state == JUMP and move_dir != 0:
            speed *= 0.7
            self.dir = -1 if move_dir < 0 else 1
        self.x += move_dir * speed * dt
        self.x = max(20, min(self.x, self.stage.bg_w - 20))
        self.vy += self.gravity_pps2 * dt
        self.y += self.vy * dt
        if self.y < self.stage.ground_y:
            self.y = self.stage.ground_y
            self.vy = 0.0
            if self.state == JUMP:
                self.state = RUN if self.ax != 0 else IDLE
                self.idle.reset()
                self.run.reset()
        if self.state == IDLE:
            self.idle.step(dt, loop=True)
        elif self.state == RUN:
            self.run.step(dt, loop=True)
        elif self.state == JUMP:
            self.jump.step(dt, loop=False)
        else:
            self.attack.step(dt, loop=False)
            if self.attack.frame >= len(self.attack.widths) - 1:
                self.state = RUN if self.ax != 0 else IDLE
                self.idle.reset()
                self.run.reset()

    def draw(self):
        if self.state == IDLE:
            self.idle.draw_world(self.stage, self.x, self.y, self.scale, flip=(self.dir == -1), foot_off_px=self.foot_idle, ground_off_px=self.ground_off)
        elif self.state == RUN:
            self.run.draw_world(self.stage, self.x, self.y, self.scale, flip=(self.dir == -1), foot_off_px=self.foot_run, ground_off_px=self.ground_off)
        elif self.state == JUMP:
            self.jump.draw_world(self.stage, self.x, self.y, self.scale, flip=(self.dir == -1), foot_off_px=self.foot_jump, ground_off_px=self.ground_off)
        else:
            self.attack.draw_world(self.stage, self.x, self.y, self.scale, flip=(self.dir == -1), foot_off_px=self.foot_attack, ground_off_px=self.ground_off)
