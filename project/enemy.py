from pico2d import *
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector
import random

EN_IDLE, EN_RUN, EN_ATTACK, EN_DEAD, EN_SPECIAL = 0, 1, 2, 3, 4


class Enemy:
    def __init__(self, stage, scale=1.0):
        self.stage = stage
        self.img_idle = load_image('enemy_idle.png')
        self.img_run = load_image('enemyrun.png')
        self.img_attack = load_image('enemyatt.png')
        self.img_dead = load_image('enemy_dead.png')
        self.img_special = load_image('special.png')
        self.img_special_slash = load_image('specialslash.png')

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

        self.data_special = dict(
            lefts=[0, self.img_special.w // 2],
            widths=[self.img_special.w // 2, self.img_special.w // 2],
            pad=0
        )

        for d in (self.data_dead, self.data_run, self.data_attack, self.data_special):
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
        self.prev_atk_frame = 0
        self.atk_tacc = 0.0
        self.atk_gap = 0.08

        self.dead_frame = 0
        self.dead_tacc = 0.0
        self.dead_gap = 0.06

        self.attack_range = 80.0
        self.attack_cooldown = 1.0
        self.attack_timer = 0.0

        self.chase_stop_dist = 40.0

        self.hit_this_swing = False
        self.hit_flash_timer = 0.0

        self.attack_start_delay_default = 0.15
        self.attack_start_delay = 0.0

        self.special_frame = 0
        self.special_phase = 0
        self.special_tacc = 0.0

        self.special_prepare_time = 0.25
        self.special_effect_time = 0.35
        self.special_appear_time = 0.15
        self.special_distance = 150.0

        self.special_teleport_x = self.x
        self.special_teleport_y = self.y

        self.special_slash_active = False
        self.special_slash_x = 0.0
        self.special_slash_y = 0.0

        self.special_recovery = 0.0
        self.special_hit_done = False

        self.special_interval_min = 10.0
        self.special_interval_max = 20.0
        self.special_timer = 0.0
        self.special_interval = 0.0

        self.reset_special_cooldown()

        self.bt = self.build_behavior_tree()

    def reset_special_cooldown(self):
        self.special_timer = 0.0
        self.special_interval = random.uniform(self.special_interval_min, self.special_interval_max)

    def is_special_ready(self):
        if self.state not in (EN_IDLE, EN_RUN):
            return False
        if self.special_recovery > 0.0:
            return False
        return self.special_timer >= self.special_interval

    def do_special(self):
        if not self.is_special_ready():
            return BehaviorTree.FAIL
        self.start_special_attack()
        self.reset_special_cooldown()
        return BehaviorTree.SUCCESS

    def build_behavior_tree(self):
        cond_special_ready = Condition('special_ready', self.is_special_ready)
        act_special = Action('do_special', self.do_special)
        special_seq = Sequence('special_seq', [cond_special_ready, act_special])

        cond_in_range = Condition('player_in_range', self.is_player_in_attack_range)
        act_attack = Action('attack', self.do_attack)
        attack_seq = Sequence('attack_seq', [cond_in_range, act_attack])

        act_chase = Action('chase_player', self.chase_player)

        root = Selector('root', [special_seq, attack_seq, act_chase])
        return BehaviorTree(root)

    def is_player_in_attack_range(self):
        player = getattr(self.stage, 'player', None)
        if player is None:
            return False
        dx = abs(player.x - self.x)
        return dx <= self.attack_range

    def do_attack(self):
        if self.state not in (EN_IDLE, EN_RUN):
            return BehaviorTree.FAIL
        player = getattr(self.stage, 'player', None)
        if player is not None:
            dx = player.x - self.x
            if dx != 0:
                self.dir = 1 if dx > 0 else -1
        self.start_attack()
        return BehaviorTree.SUCCESS

    def chase_player(self):
        if self.state == EN_DEAD:
            return BehaviorTree.FAIL
        player = getattr(self.stage, 'player', None)
        if player is None:
            return BehaviorTree.FAIL
        dx = player.x - self.x
        if abs(dx) < self.chase_stop_dist:
            if self.state == EN_RUN:
                self.stop_run()
            return BehaviorTree.SUCCESS
        self.dir = 1 if dx > 0 else -1
        if self.state != EN_RUN:
            self.start_run()
        return BehaviorTree.RUNNING

    def handle_collision(self, group, other, hit):
        if group == 'player:enemy' and hit:
            self.die()

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

    def is_intersect(self, aabb):
        l1, b1, r1, t1 = self.aabb()
        l2, b2, r2, t2 = aabb
        if l1 > r2:
            return False
        if r1 < l2:
            return False
        if t1 < b2:
            return False
        if b1 > t2:
            return False
        return True

    def attack_hitbox(self):
        fw = 40.0 * self.char_scale
        fh = 30.0 * self.char_scale
        off_x = 20.0 * self.char_scale
        off_y = 20.0 * self.char_scale
        if self.dir == 1:
            l = self.x + off_x
            r = l + fw
        else:
            r = self.x - off_x
            l = r - fw
        b = self.y + off_y
        t = b + fh
        return l, b, r, t

    def check_player_hit(self):
        if self.hit_this_swing:
            return
        player = getattr(self.stage, 'player', None)
        if player is None:
            return
        if not player.is_vulnerable():
            return
        atk_l, atk_b, atk_r, atk_t = self.attack_hitbox()
        pl_l, pl_b, pl_r, pl_t = player.get_bb()
        if atk_l > pl_r:
            return
        if atk_r < pl_l:
            return
        if atk_t < pl_b:
            return
        if atk_b > pl_t:
            return
        self.hit_this_swing = True
        self.hit_flash_timer = 0.2
        setattr(player, 'last_hit_by_enemy', self)
        player.hit_flash_timer = 0.2
        if hasattr(player, 'die'):
            player.die()

    def check_special_hit(self):
        player = getattr(self.stage, 'player', None)
        if player is None:
            return
        if not player.is_vulnerable():
            return
        setattr(player, 'last_hit_by_enemy', self)
        player.hit_flash_timer = 0.2
        if hasattr(player, 'die'):
            player.die()


    def stop_run(self):
        if self.state != EN_DEAD:
            self.state = EN_IDLE
            self.frame = 0
            self.tacc = 0.0

    def start_run(self):
        if self.state != EN_DEAD and self.state != EN_RUN:
            self.state = EN_RUN
            self.run_frame = 0
            self.run_tacc = 0.0

    def start_attack(self):
        if self.state != EN_DEAD:
            self.state = EN_ATTACK
            self.prev_atk_frame = 0
            self.atk_frame = 0
            self.atk_tacc = 0.0
            self.hit_this_swing = False
            self.attack_start_delay = self.attack_start_delay_default

    def start_special_attack(self):
        if self.state == EN_DEAD:
            return
        self.state = EN_SPECIAL
        self.special_frame = 0
        self.special_phase = 0
        self.special_tacc = 0.0

        player = getattr(self.stage, 'player', None)

        teleport_x = self.x + self.dir * 150.0
        teleport_x = max(20, min(self.stage.w - 20, teleport_x))
        self.special_teleport_x = teleport_x
        self.special_teleport_y = self.y

        if player is not None:
            self.special_slash_x = player.x
            self.special_slash_y = player.y + self.ground_off + 35
        else:
            self.special_slash_x = self.x + self.dir * (self.special_distance * 0.5)
            self.special_slash_y = self.y + 35

        self.special_slash_active = False
        self.special_hit_done = False

    def update(self, dt):
        self.stage.apply_physics(self, dt, 0)

        if self.state != EN_DEAD:
            self.special_timer += dt

        if self.special_recovery > 0.0:
            self.special_recovery -= dt
            if self.special_recovery < 0:
                self.special_recovery = 0
            self.state = EN_IDLE
            self.tacc += dt
            while self.tacc >= self.gap:
                self.tacc -= self.gap
                self.frame = (self.frame + 1) % self.idle_cols
            return

        if self.attack_timer > 0.0:
            self.attack_timer -= dt
            if self.attack_timer < 0.0:
                self.attack_timer = 0.0

        if self.hit_flash_timer > 0.0:
            self.hit_flash_timer -= dt
            if self.hit_flash_timer < 0.0:
                self.hit_flash_timer = 0.0

        if self.state == EN_DEAD:
            self.dead_tacc += dt
            while self.dead_tacc >= self.dead_gap:
                self.dead_tacc -= self.dead_gap
                if self.dead_frame < len(self.data_dead['widths']) - 1:
                    self.dead_frame += 1
            return

        if self.state in (EN_IDLE, EN_RUN) and self.attack_timer <= 0.0:
            self.bt.run()
        elif self.state in (EN_IDLE, EN_RUN):
            self.chase_player()

        if self.state == EN_IDLE:
            self.tacc += dt
            while self.tacc >= self.gap:
                self.tacc -= self.gap
                self.frame = (self.frame + 1) % self.idle_cols

        elif self.state == EN_RUN:
            self.run_tacc += dt
            while self.run_tacc >= self.run_gap:
                self.run_tacc -= self.run_gap
                self.run_frame = (self.run_frame + 1) % len(self.data_run['widths'])
            self.x += self.dir * self.speed * dt

        elif self.state == EN_ATTACK:
            if self.attack_start_delay > 0.0:
                self.attack_start_delay -= dt
                if self.attack_start_delay < 0.0:
                    self.attack_start_delay = 0.0
                return

            self.atk_tacc += dt
            while self.atk_tacc >= self.atk_gap:
                self.atk_tacc -= self.atk_gap
                self.prev_atk_frame = self.atk_frame
                self.atk_frame += 1

                if 2 <= self.atk_frame <= 4:
                    self.check_player_hit()

                if self.atk_frame >= len(self.data_attack['widths']):
                    self.atk_frame = 0
                    self.state = EN_IDLE
                    self.attack_timer = self.attack_cooldown
                    break

        elif self.state == EN_SPECIAL:
            self.special_tacc += dt

            if self.special_phase == 0:
                if self.special_tacc >= self.special_prepare_time:
                    self.special_tacc = 0.0
                    self.special_phase = 1
                    self.special_slash_active = True

            elif self.special_phase == 1:
                if not self.special_hit_done:
                    self.check_special_hit()
                    self.special_hit_done = True

                if self.special_tacc >= self.special_effect_time:
                    self.special_tacc = 0.0
                    self.special_phase = 2
                    self.special_slash_active = False
                    self.special_frame = 1
                    self.x = self.special_teleport_x
                    self.y = self.special_teleport_y

            else:
                if self.special_tacc >= self.special_appear_time:
                    self.special_tacc = 0.0
                    self.attack_timer = self.attack_cooldown
                    self.stop_run()
                    self.special_recovery = 1.0

    def draw(self):
        flip = (self.dir == -1)
        if self.state == EN_IDLE:
            self.stage.draw_strip(self.img_idle, self.idle_cols, self.frame,
                                  self.x, self.y, self.char_scale, flip)
        elif self.state == EN_RUN:
            self.stage.draw_frame(self.img_run, self.data_run, self.run_frame,
                                  self.x, self.y + 3, self.char_scale, flip)
        elif self.state == EN_ATTACK:
            self.stage.draw_frame(self.img_attack, self.data_attack, self.atk_frame,
                                  self.x, self.y, self.char_scale, flip)
        elif self.state == EN_SPECIAL:
            if self.special_phase == 0:
                idx = 0
            elif self.special_phase == 2:
                idx = 1
            else:
                idx = None
            if idx is not None:
                self.stage.draw_frame(self.img_special, self.data_special, idx,
                                      self.x, self.y, self.char_scale, flip)
        else:
            self.stage.draw_frame(self.img_dead, self.data_dead, self.dead_frame,
                                  self.x, self.y, self.char_scale, False)

        l, b, r, t = self.get_bb()
        sx1, sy1 = self.stage.to_screen(l, b)
        sx2, sy2 = self.stage.to_screen(r, t)
        draw_rectangle(sx1, sy1, sx2, sy2)

        if self.state == EN_ATTACK:
            atk_l, atk_b, atk_r, atk_t = self.attack_hitbox()
            ax1, ay1 = self.stage.to_screen(atk_l, atk_b)
            ax2, ay2 = self.stage.to_screen(atk_r, atk_t)
            draw_rectangle(ax1, ay1, ax2, ay2)

        if self.special_slash_active:
            sx, sy = self.stage.to_screen(self.special_slash_x, self.special_slash_y)
            w = self.img_special_slash.w * self.char_scale
            h = self.img_special_slash.h * self.char_scale
            flip_flag = 'h' if self.dir == -1 else ''
            self.img_special_slash.clip_composite_draw(
                0, 0,
                self.img_special_slash.w, self.img_special_slash.h,
                0,
                flip_flag,
                sx, sy,
                w, h
            )
