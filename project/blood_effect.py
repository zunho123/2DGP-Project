from pico2d import *
import random


class BloodEffect:
    images = None

    def __init__(self, stage, x, y, kind=None, scale=1.0, frame_gap=0.04):
        self.stage = stage
        if BloodEffect.images is None:
            BloodEffect.images = [
                load_image('blood_1.png'),
                load_image('blood_2.png'),
                load_image('blood_3.png')
            ]
        if kind is None:
            self.img = random.choice(BloodEffect.images)
        else:
            self.img = BloodEffect.images[kind % len(BloodEffect.images)]
        self.x = x
        self.y = y
        self.scale = scale
        self.cols = 4
        self.frame = 0
        self.tacc = 0.0
        self.gap = frame_gap
        self.alive = True

    def update(self, dt):
        if not self.alive:
            return
        self.tacc += dt
        while self.tacc >= self.gap:
            self.tacc -= self.gap
            self.frame += 1
            if self.frame >= self.cols:
                self.alive = False
                break

    def is_alive(self):
        return self.alive

    def draw(self):
        if not self.alive:
            return
        self.stage.draw_strip(self.img, self.cols, self.frame, self.x, self.y, self.scale, False)
