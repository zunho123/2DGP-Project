from pico2d import *

class SpriteAnim:
    def __init__(self, img_path, lefts, widths, pad=0):
        self.img = load_image(img_path)
        self.lefts = lefts
        self.widths = widths
        self.pad = pad
        eff = [max(1, w - 2 * pad) for w in widths]
        self.aw = sum(eff) / len(eff)
        self.frame = 0
        self.tacc = 0.0
        self.gap = 0.06

    def set_gap(self, gap):
        self.gap = gap

    def reset(self):
        self.frame = 0
        self.tacc = 0.0

    def step(self, dt, loop=True):
        self.tacc += dt
        while self.tacc >= self.gap:
            self.frame += 1
            self.tacc -= self.gap
        if loop:
            self.frame %= len(self.widths)
        else:
            if self.frame >= len(self.widths):
                self.frame = len(self.widths) - 1

    def draw_world(self, stage, x, y, scale, flip=False, foot_off_px=0, ground_off_px=0):
        i = self.frame
        w_src = self.widths[i] - 2 * self.pad
        l_src = self.lefts[i] + self.pad
        h = self.img.h
        sx = stage.window_w / stage.vw
        sy = stage.window_h / stage.vh
        dw = int(w_src * scale * sx)
        dh = int(h * scale * sy)
        cx = (x + ((w_src - self.aw) / 2)) - stage.left
        cy = y - stage.bottom
        sxp = int(cx * sx)
        syp = int(cy * sy) + dh // 2 - int(foot_off_px * scale * sy) - int(ground_off_px * scale * sy)
        if flip:
            self.img.clip_composite_draw(l_src, 0, w_src, h, 0, 'h', sxp, syp, dw, dh)
        else:
            self.img.clip_draw(l_src, 0, w_src, h, sxp, syp, dw, dh)
