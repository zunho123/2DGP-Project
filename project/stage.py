from pico2d import *

class Stage:
    def __init__(self, bg_path, window_w=1280, window_h=720, zoom=1.6, ground_px=36):
        self.win_w = window_w
        self.win_h = window_h
        self.bg = load_image(bg_path)
        self.w, self.h = self.bg.w, self.bg.h
        self.zoom = zoom
        self.vw = self.win_w / self.zoom
        self.vh = self.win_h / self.zoom
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.ground_y = ground_px
        self.platforms = [(0, self.w, self.ground_y), (96, self.w - 96, int(self.h * 0.5))]
        self.edge_margin = 6
        self.follow_k = 8.0

    def clamp(self, v, lo, hi):
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    def to_screen(self, x, y):
        sx = self.win_w / self.vw
        sy = self.win_h / self.vh
        return int((x - self.cam_x) * sx), int((y - self.cam_y) * sy)

    def draw_bg(self):
        left = int(self.cam_x)
        bottom = int(self.cam_y)
        self.bg.clip_draw(left, bottom, int(self.vw), int(self.vh), self.win_w // 2, self.win_h // 2, self.win_w, self.win_h)

    def draw(self):
        self.draw_bg()

    def update(self, dt, focus_x):
        target = self.clamp(focus_x - self.vw * 0.5, 0, max(0, self.w - self.vw))
        self.cam_x += (target - self.cam_x) * min(1.0, dt * self.follow_k)

    def platform_under(self, x, y, off=0, tol=2.0):
        for x1, x2, py in sorted(self.platforms, key=lambda t: t[2], reverse=True):
            if x1 <= x <= x2 and abs(y - (py + off)) <= tol:
                return py
        return None

    def snap_to_platform(self, x, prev_y, new_y, off=0):
        landed = False
        support = None
        for x1, x2, py in sorted(self.platforms, key=lambda t: t[2], reverse=True):
            if x1 <= x <= x2:
                line = py + off
                if prev_y >= line and new_y <= line:
                    new_y = line
                    landed = True
                    support = py
                    break
        return new_y, landed, support

    def apply_physics(self, actor, dt, move_dir):
        prev_y = actor.y
        actor.x += move_dir * actor.run_speed * dt
        actor.x = self.clamp(actor.x, self.edge_margin, self.w - self.edge_margin)
        actor.vy += actor.gravity * dt
        new_y = actor.y + actor.vy * dt
        new_y, landed, support = self.snap_to_platform(actor.x, prev_y, new_y, actor.ground_off)
        actor.y = new_y
        if landed:
            actor.vy = 0.0
            actor.on_ground = True
        else:
            actor.on_ground = False

    def draw_strip(self, img, cols, fi, x, y, scale=1.0, flip=False, pad=0):
        fh = img.h
        if pad > 0:
            fw = (img.w - pad * (cols + 1)) // cols
            l_src = pad + (fw + pad) * (fi % cols)
            w_src = fw
        else:
            fw = img.w // cols
            l_src = fw * (fi % cols)
            w_src = fw
        sx, sy = self.to_screen(x, y)
        dw = int(w_src * scale * (self.win_w / self.vw))
        dh = int(fh * scale * (self.win_h / self.vh))
        if flip:
            img.clip_composite_draw(l_src, 0, w_src, fh, 0, 'h', sx, sy + dh // 2, dw, dh)
        else:
            img.clip_draw(l_src, 0, w_src, fh, sx, sy + dh // 2, dw, dh)

    def draw_frame(self, img, meta, fi, x, y, scale=1.0, flip=False):
        pad = meta.get('pad', 0)
        w_src = meta['widths'][fi] - 2 * pad
        l_src = meta['lefts'][fi] + pad
        h = img.h
        aw = meta['aw']
        sx, sy = self.to_screen(x + ((w_src - aw) * 0.5), y)
        dw = int(w_src * scale * (self.win_w / self.vw))
        dh = int(h * scale * (self.win_h / self.vh))
        if flip:
            img.clip_composite_draw(l_src, 0, w_src, h, 0, 'h', sx, sy + dh // 2, dw, dh)
        else:
            img.clip_draw(l_src, 0, w_src, h, sx, sy + dh // 2, dw, dh)
