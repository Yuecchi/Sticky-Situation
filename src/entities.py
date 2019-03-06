try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import gfx
from enum import Enum

TILESIZE = 32
HALFSIZE = 16
TILE_DIMS = (TILESIZE, TILESIZE)

class Sprite:

    def __init__(self, img):
        self.img = img
        self.cols = self.img.get_width() / TILESIZE

        self.animation = ([0, 0], [0, 0])
        self.animation_speed = 1
        self.current_index = self.animation[0].copy()

    def set_animation(self, animation):
        self.snimation = animation

    def set_animation_speed(self, speed):
        self.animation_speed = speed

    def draw(self, canvas, map_pos):
        pos = (HALFSIZE + (map_pos.x * TILESIZE), HALFSIZE + (map_pos.y * TILESIZE))
        src_pos = (HALFSIZE + (self.current_index[0] * TILESIZE), HALFSIZE + (self.current_index[1] * TILESIZE))
        canvas.draw_image(self.img, src_pos, TILE_DIMS, pos, TILE_DIMS)

        if gfx.clock.transition(self.animation_speed): self.next_frame()

    def next_frame(self):
        if self.current_index == self.animation[1]:
            self.current_index = self.animation[0].copy()
        else:
            self.current_index[0] = (self.current_index[0] + 1) % self.cols
            if self.current_index[0] == 0: self.current_index[1] += 1

class Entity:

    def __init__(self, pos, img):
        self.pos = pos
        self.img = img
        self.sprite = Sprite(self.img)

    def draw(self, canvas):
        self.sprite.draw(canvas, self.pos)

class PlayerState(Enum):
    IDLE = 0

class Player(Entity):

    def __init__(self, pos, img):

        Entity.__init__(self, pos, img)
