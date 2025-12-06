from pico2d import *

IDLE, RUN, JUMP, ATTACK, ROLL, DEAD, STAND = 0, 1, 2, 3, 4, 5, 6


class Player:
    def __init__(self, stage, scale=1.0):
        self.stage = stage
        self.img_idle = load_image('idle.png')
        self.img_run = load_image('run.png')
        self.img_jump = load_image('jump.png')
        self.img_attack = load_image('attack.png')
        self.img_roll = load_image('rolling.png')
        self.img_dead = load_image('player_dead.png')
        self.img_stand = load_image('player_stand.png')

        self.data_idle = dict(
            lefts=[8, 45, 84, 123, 162, 202, 242, 282, 321, 360],
            widths=[31, 31, 32, 32, 33, 33, 33, 32, 32, 31],
            pad=1
        )
        self.data_run = dict(
            lefts=[11, 55, 98, 141, 184, 227, 271, 314, 359, 405],
            widths=[39, 38, 38, 38, 38, 39, 38, 40, 41, 41],
            pad=1
        )
        self.data_jump = dict(
            lefts=[11, 45, 80, 115, 168, 214, 260, 306],
            widths=[29, 30, 30, 29, 41, 41, 41, 41],
            pad=1
        )
        self.data_attack = dict(
            lefts=[12, 57, 111, 158, 207, 254, 303],
            widths=[38, 47, 40, 42, 40, 42, 42],
            pad=0
        )
        self.data_roll = dict(
            lefts=[11, 63, 104, 145, 187, 232, 283],
            widths=[47, 37, 36, 37, 40, 46, 43],
            pad=0
        )
        self.data_dead = dict(
            lefts=[11, 54, 111, 163, 218, 271, 325, 373, 435, 494, 552, 609],
            widths=[38, 33, 47, 50, 48, 47, 43, 57, 55, 53, 52, 54],
            pad=1
        )
        self.data_stand = dict(
            lefts=[11, 65, 110, 154, 202, 250, 292, 341, 382],
            widths=[49, 40, 39, 43, 43, 37, 44, 36, 35],
            pad=1
        )

        for d in (self.data_idle, self.data_run, self.data_jump,
                  self.data_attack, self.data_roll, self.data_dead, self.data_stand):
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
        self.prev_atk_frame = 0

        self.tacc = 0.0
        self.atk_tacc = 0.0
        self.roll_frame = 0
        self.roll_tacc = 0.0
        self.dead_frame = 0
        self.dead_tacc = 0.0
        self.dead_gap = 0.06
        self.stand_frame = 0
        self.stand_tacc = 0.0
        self.stand_gap = 0.06

        self.run_speed = 260.0
        self.gravity = -2000.0
        self.jump_vel = 520.0
        self.vy = 0.0
        self.on_ground = True

        self.slash_img = load_image('slash.png')
        self.slash_cols = 5
        self.slash_frame = 0
        self.slash_tacc = 0.0
        self.slash_playing = False

        self.invincible = False
        self.hit_flash_timer = 0.0
        self.last_hit_by_enemy = None
        self.stage.player = self
        self.dead_time = -1.0

    def request_jump(self):
        if self.state in (DEAD, STAND):
            return
        if self.on_ground and self.state not in (ATTACK, ROLL):
            self.state = JUMP
            self.vy = self.jump_vel
            self.jump_frame = 0
            self.tacc = 0.0

    def request_attack(self):
        if self.state in (DEAD, STAND):
            return
        if self.state not in (ATTACK, ROLL):
            self.state = ATTACK
            self.prev_atk_frame = 0
            self.atk_frame = 0
            self.atk_tacc = 0.0
            self.slash_playing = False

    def request_roll(self):
        if self.state in (DEAD, STAND):
            return
        if self.on_ground and (self.state == IDLE or self.state == RUN):
            self.state = ROLL
            self.roll_frame = 0
            self.roll_tacc = 0.0
            self.invincible = True


    def is_attacking_active(self):
        return self.state == ATTACK and 2 <= self.atk_frame <= 5

    def attack_hitbox(self):
        fw = 28.0 * self.char_scale
        fh = 22.0 * self.char_scale
        off = 6.0 * self.char_scale
        if self.dir == 1:
            l = self.x + off
            r = self.x + off + fw
        else:
            l = self.x - off - fw
            r = self.x - off
        b = self.y + 26.0 * self.char_scale
        t = b + fh
        return l, b, r, t

    def get_bb(self):
        w = 30.0 * self.char_scale - 4
        h = 70.0 * self.char_scale - 22
        l = self.x - w * 0.5
        r = self.x + w * 0.5
        b = self.y + 14
        t = self.y + h
        return l, b, r, t

    def is_vulnerable(self):
        return (not self.invincible) and self.state not in (DEAD, STAND)

    def die(self):
        if self.state == DEAD:
            return
        self.state = DEAD
        self.dead_frame = 0
        self.dead_tacc = 0.0
        self.vy = 0.0
        self.invincible = False
        self.slash_playing = False
        self.dead_time = 0.0

    def start_stand(self):
        self.state = STAND
        self.stand_frame = 0
        self.stand_tacc = 0.0
        self.vy = 0.0
        self.invincible = False
        self.slash_playing = False
        self.dead_time = -1.0

    def update(self, dt, move_dir=0):
        if self.state == DEAD:
            self.stage.apply_physics(self, dt, 0)
            if self.dead_time >= 0.0:
                self.dead_time += dt
            if self.hit_flash_timer > 0.0:
                self.hit_flash_timer -= dt
                if self.hit_flash_timer < 0.0:
                    self.hit_flash_timer = 0.0
            self.dead_tacc += dt
            while self.dead_tacc >= self.dead_gap:
                self.dead_tacc -= self.dead_gap
                if self.dead_frame < len(self.data_dead['widths']) - 1:
                    self.dead_frame += 1
            return

        if move_dir != 0:
            self.dir = 1 if move_dir > 0 else -1

        if self.state not in (JUMP, ATTACK, ROLL, STAND):
            if move_dir != 0:
                self.state = RUN
            else:
                self.state = IDLE

        phys_dir = move_dir
        if self.state == ROLL and phys_dir == 0:
            phys_dir = self.dir
        if self.state == STAND:
            phys_dir = 0
        self.stage.apply_physics(self, dt, phys_dir)

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

        elif self.state == ROLL:
            self.roll_tacc += dt
            while self.roll_tacc >= 0.05:
                self.roll_tacc -= 0.05
                self.roll_frame += 1
                if self.roll_frame >= len(self.data_roll['widths']):
                    self.invincible = False
                    if self.on_ground:
                        self.state = RUN if move_dir != 0 else IDLE
                        self.frame = 0
                        self.tacc = 0.0
                    else:
                        self.state = JUMP
                    self.roll_frame = 0
                    break

        elif self.state == ATTACK:
            self.atk_tacc += dt
            while self.atk_tacc >= 0.045:
                self.atk_tacc -= 0.045
                self.prev_atk_frame = self.atk_frame
                self.atk_frame += 1

                if self.prev_atk_frame < 2 <= self.atk_frame:
                    self.slash_playing = True
                    self.slash_frame = 0
                    self.slash_tacc = 0.0

                if self.atk_frame >= len(self.data_attack['widths']):
                    if self.on_ground:
                        self.state = RUN if move_dir != 0 else IDLE
                        self.frame = 0
                        self.tacc = 0.0
                    else:
                        self.state = JUMP
                    self.atk_frame = 0
                    break

        elif self.state == STAND:
            self.stand_tacc += dt
            while self.stand_tacc >= self.stand_gap:
                self.stand_tacc -= self.stand_gap
                if self.stand_frame < len(self.data_stand['widths']) - 1:
                    self.stand_frame += 1
                else:
                    self.state = IDLE
                    self.frame = 0
                    self.tacc = 0.0
                    break

        if self.slash_playing:
            self.slash_tacc += dt
            while self.slash_tacc >= 0.03:
                self.slash_tacc -= 0.03
                self.slash_frame += 1
                if self.slash_frame >= self.slash_cols:
                    self.slash_playing = False
                    break

        if self.hit_flash_timer > 0.0:
            self.hit_flash_timer -= dt
            if self.hit_flash_timer < 0.0:
                self.hit_flash_timer = 0.0

    def draw(self):
        flip = (self.dir == -1)

        if self.state == IDLE:
            self.stage.draw_frame(self.img_idle, self.data_idle, self.frame,
                                  self.x, self.y, self.char_scale, flip)

        elif self.state == RUN:
            self.stage.draw_frame(self.img_run, self.data_run, self.frame,
                                  self.x, self.y, self.char_scale, flip)

        elif self.state == JUMP:
            self.stage.draw_frame(self.img_jump, self.data_jump, self.jump_frame,
                                  self.x, self.y, self.char_scale, flip)

        elif self.state == ROLL:
            self.stage.draw_frame(self.img_roll, self.data_roll, self.roll_frame,
                                  self.x, self.y - 5, self.char_scale, flip)

        elif self.state == DEAD:
            self.stage.draw_frame(self.img_dead, self.data_dead, self.dead_frame,
                                  self.x, self.y + 2, self.char_scale, flip)

        elif self.state == STAND:
            self.stage.draw_frame(self.img_stand, self.data_stand, self.stand_frame,
                                  self.x, self.y + 7.5, self.char_scale, flip)

        else:
            self.stage.draw_frame(self.img_attack, self.data_attack, self.atk_frame,
                                  self.x, self.y, self.char_scale, flip)

        if self.slash_playing:
            offset_x = 20.0 * self.char_scale * self.dir
            offset_y = 26.0 * self.char_scale
            ex = self.x + offset_x
            ey = self.y + offset_y
            self.stage.draw_strip(
                self.slash_img,
                self.slash_cols,
                self.slash_frame,
                ex,
                ey,
                self.char_scale,
                flip=(self.dir == -1),
                pad=0
            )


