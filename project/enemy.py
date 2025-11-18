from pico2d import *

EN_IDLE, EN_RUN, EN_ATTACK, EN_DEAD = 0, 1, 2, 3


class Enemy:
    def __init__(self, stage, scale=1.0):
        self.stage = stage
        self.img_idle = load_image('enemy_idle.png')
        self.img_run = load_image('enemyrun.png')
        self.img_attack = load_image('enemyatt.png')
        self.img_dead = load_image('enemy_dead.png')

        self.idle_cols = 12

        self.data_dead = dict(
            lefts=[13, 48, 89, 132, 175, 218, 274, 325, 394, 459, 523, 588],
            widths=[32, 35, 41, 41, 41, 41, 40, 65, 57, 55, 56, 55],
            pad=1
        )

        self.data_run = dict(
            lefts=[7, 48, 93, 138, 186, 232, 279, 324, 368, 417],
            widths=[33, 39, 39, 41, 44, 44, 38, 38, 40, 37],
            pad=0
        )

        self.data_attack = dict(
            lefts=[8, 62, 129, 187, 245, 300],
            widths=[41, 56, 47, 47, 47, 47],
            pad=0
        )

        for d in (self.data_dead, self.data_run, self.data_attack):
            pad = d.get('pad', 0)
            eff = [max(1, w - 2 * pad) for w in d['widths']]
            d['aw'] = sum(eff) / len(eff)

        self.char_scale = scale
        self.x = min(stage.w - 20, stage.w // 2 + 140)
        self.ground_off = 5
        self.y = stage.ground_y + self.ground_off + 2
        self.dir = -1

        self.speed = 120.0
        self.run_speed = 0.0
        self.gravity = -2000.0
        self.vy = 0.0
        self.on_ground = True

        self.state = EN_RUN

        self.frame = 0
        self.tacc = 0.0
        self.gap = 0.08

        self.run_frame = 0
        self.run_tacc = 0.0
        self.run_gap = 0.06

        self.atk_frame = 0
        self.atk_tacc = 0.0
        self.atk_gap = 0.06

        self.dead_frame = 0
        self.dead_tacc = 0.0
        self.dead_gap = 0.06

        self.ai_attack_interval = 2.0
        self.ai_attack_timer = 0.0

        patrol_range = 140.0
        left = self.x - patrol_range * 0.5
        right = self.x + patrol_range * 0.5
        self.patrol_left = max(40.0, left)
        self.patrol_right = min(self.stage.w - 40.0, right)

        self.idle_time = 0.0
        self.idle_duration = 2.0

    def is_alive(self):
        return self.state != EN_DEAD

    def die(self):
        if self.state != EN_DEAD:
            self.state = EN_DEAD
            self.dead_frame = 0
            self.dead_tacc = 0.0
            self.vy = 0.0

    def is_dead(self):
        return self.state == EN_DEAD

    def aabb(self):
        fw = (self.img_idle.w // self.idle_cols) * self.char_scale * 0.6
        fh = self.img_idle.h * self.char_scale * 0.8 + 5
        l = self.x - fw * 0.5
        r = self.x + fw * 0.5
        b = self.y + 8
        t = self.y + fh
        return l, b, r, t

    def get_bb(self):
        return self.aabb()

    def start_run(self):
        if self.state != EN_DEAD:
            self.state = EN_RUN
            self.run_frame = 0
            self.run_tacc = 0.0

    def stop_run(self):
        if self.state != EN_DEAD:
            self.state = EN_IDLE
            self.frame = 0
            self.tacc = 0.0
            self.idle_time = 0.0

    def start_attack(self):
        if self.state != EN_DEAD:
            self.state = EN_ATTACK
            self.atk_frame = 0
            self.atk_tacc = 0.0

    def update(self, dt):
        self.stage.apply_physics(self, dt, 0)

        if self.state == EN_DEAD:
            self.dead_tacc += dt
            while self.dead_tacc >= self.dead_gap:
                self.dead_tacc -= self.dead_gap
                if self.dead_frame < len(self.data_dead['widths']) - 1:
                    self.dead_frame += 1
            return

        self.ai_attack_timer += dt
        if self.state in (EN_IDLE, EN_RUN) and self.ai_attack_timer >= self.ai_attack_interval:
            self.start_attack()
            self.ai_attack_timer = 0.0

        if self.state == EN_IDLE:
            self.idle_time += dt

            self.tacc += dt
            while self.tacc >= self.gap:
                self.tacc -= self.gap
                self.frame = (self.frame + 1) % self.idle_cols

            if self.idle_time >= self.idle_duration:
                self.idle_time = 0.0
                self.start_run()

        elif self.state == EN_RUN:
            self.run_tacc += dt
            while self.run_tacc >= self.run_gap:
                self.run_tacc -= self.run_gap
                self.run_frame = (self.run_frame + 1) % len(self.data_run['widths'])

            self.x += self.dir * self.speed * dt

            if self.x < self.patrol_left:
                self.x = self.patrol_left
                self.dir = 1
                self.stop_run()
            elif self.x > self.patrol_right:
                self.x = self.patrol_right
                self.dir = -1
                self.stop_run()

        elif self.state == EN_ATTACK:
            self.atk_tacc += dt
            while self.atk_tacc >= self.atk_gap:
                self.atk_tacc -= self.atk_gap
                self.atk_frame += 1
                if self.atk_frame >= len(self.data_attack['widths']):
                    self.atk_frame = 0
                    self.start_run()
                    break

    def draw(self):
        flip = (self.dir == -1)
        if self.state == EN_IDLE:
            self.stage.draw_strip(self.img_idle, self.idle_cols, self.frame,
                                  self.x, self.y, self.char_scale, flip, pad=0)
        elif self.state == EN_RUN:
            self.stage.draw_frame(self.img_run, self.data_run, self.run_frame,
                                  self.x, self.y + 3, self.char_scale, flip)
        elif self.state == EN_ATTACK:
            self.stage.draw_frame(self.img_attack, self.data_attack, self.atk_frame,
                                  self.x, self.y, self.char_scale, flip)
        else:
            self.stage.draw_frame(self.img_dead, self.data_dead, self.dead_frame,
                                  self.x, self.y, self.char_scale, False)

        l, b, r, t = self.get_bb()
        sx1, sy1 = self.stage.to_screen(l, b)
        sx2, sy2 = self.stage.to_screen(r, t)
        draw_rectangle(sx1, sy1, sx2, sy2)
