from pico2d import *

class Player:
    def __init__(self, stage, scale=1.0):
        self.stage = stage
        self.img_idle = load_image('idle.png')
        self.img_run = load_image('run.png')
        self.img_jump = load_image('jump.png')
        self.img_attack = load_image('attack.png')
        self.data_idle = dict(lefts=[8,45,84,123,162,202,242,282,321,360], widths=[31,31,32,32,33,33,33,32,32,31], pad=1)
        self.data_run = dict(lefts=[11,55,98,141,184,227,271,314,359,405], widths=[39,38,38,38,38,39,38,40,41,41], pad=1)
        self.data_jump = dict(lefts=[11,45,80,115,168,214,260,306], widths=[29,30,30,29,41,41,41,41], pad=1)
        self._finalize(self.data_idle)
        self._finalize(self.data_run)
        self._finalize(self.data_jump)
        self.char_scale = scale
        self.x = self.stage.w // 2
        self.ground_off = 0
        self.y = self.stage.ground_y + self.ground_off
        self.dir = 1
        self.state = 'idle'
        self.frame = 0
        self.jump_frame = 0
        self.tacc = 0.0
        self.run_speed = 260.0
        self.gravity = -2000.0
        self.jump_vel = 520.0
        self.vy = 0.0
        self.on_ground = True

    def _finalize(self, meta):
        pad = meta.get('pad', 0)
        eff = [max(1, w - 2 * pad) for w in meta['widths']]
        meta['aw'] = sum(eff) / len(eff)

    def request_jump(self):
        if self.on_ground and self.state != 'attack':
            self.state = 'jump'
            self.vy = self.jump_vel
            self.jump_frame = 0
            self.tacc = 0.0

    def request_attack(self):
        pass

    def update(self, dt, move_dir):
        if self.state != 'jump':
            if move_dir != 0:
                self.state = 'run'
                self.dir = 1 if move_dir > 0 else -1
            else:
                self.state = 'idle'
        self.stage.apply_physics(self, dt, move_dir)
        if self.state == 'idle':
            gap = 0.08
            self.tacc += dt
            if self.tacc >= gap:
                self.tacc -= gap
                self.frame = (self.frame + 1) % len(self.data_idle['widths'])
        elif self.state == 'run':
            gap = 0.04
            self.tacc += dt
            if self.tacc >= gap:
                self.tacc -= gap
                self.frame = (self.frame + 1) % len(self.data_run['widths'])
        else:
            gap = 0.06
            self.tacc += dt
            if self.tacc >= gap:
                self.tacc -= gap
                self.jump_frame = min(self.jump_frame + 1, len(self.data_jump['widths']) - 1)
            if self.on_ground:
                self.state = 'run' if move_dir != 0 else 'idle'
                self.frame = 0
                self.tacc = 0.0

    def draw(self):
        if self.state == 'idle':
            self.stage.draw_frame(self.img_idle, self.data_idle, self.frame, self.x, self.y, self.char_scale, self.dir == -1)
        elif self.state == 'run':
            self.stage.draw_frame(self.img_run, self.data_run, self.frame, self.x, self.y, self.char_scale, self.dir == -1)
        else:
            self.stage.draw_frame(self.img_jump, self.data_jump, self.jump_frame, self.x, self.y, self.char_scale, self.dir == -1)
