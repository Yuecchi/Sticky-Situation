try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import gfx
import tileEngine
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

    entities = []
    next_id = 1

    def __init__(self, pos, img):

        self.id = Entity.next_id
        Entity.next_id += 1

        self.pos = pos
        self.img = img
        self.sprite = Sprite(self.img)

        # add to list of entities
        Entity.entities.append(self)

    def draw(self, canvas):
        self.sprite.draw(canvas, self.pos)

class Player(Entity):

    ENTITY_TYPE = 1

    def __init__(self, pos, img, entity_map, tilemap):

        Entity.__init__(self, pos, img)

        # TODO: THIS IS HEAVILY LIKELY TO BE CHANGED
        self.entity_map = entity_map
        self.tilemap = tilemap
        entity_map[pos.y][pos.x] = self.id

    def move(self, newpos):
        can_move = True

        # check if the move is within the boundaries of the map?
        # check tile as self.pos?
        # check tile at newpos
        tile = self.tilemap.map[newpos.y][newpos.x]
        if self.tilemap.tilesheet.tiles[tile].type == tileEngine.SOLID:
            can_move = False
        # if ice, move in direction until not ice
        # check entity at newpos

        entity_id = self.entity_map[newpos.y][newpos.x]
        if bool(entity_id):
            entity = Entity.entities[entity_id - 1]
            if entity.ENTITY_TYPE == 2:
                pushpos = newpos - self.pos
                can_move = entity.move(entity.pos + pushpos)



        # if all checks are fine, move
        if can_move:
            self.entity_map[self.pos.y][self.pos.x] = 0
            self.entity_map[newpos.y][newpos.x] = self.id
            self.pos = newpos

class PushBlock(Entity):

    ENTITY_TYPE = 2

    def __init__(self, pos, img, entity_map, tilemap):

        Entity.__init__(self, pos, img)

        # may be different when level class is implemented
        self.entity_map = entity_map
        self.tilemap = tilemap
        entity_map[pos.y][pos.x] = self.id

    def move(self, newpos):
        can_move = True
        # check tile at newpos
        tile = self.tilemap.map[newpos.y][newpos.x]
        if self.tilemap.tilesheet.tiles[tile].type == tileEngine.SOLID:
            can_move = False
        # if all checks are fine, move
        if can_move:
            self.entity_map[self.pos.y][self.pos.x] = 0
            self.entity_map[newpos.y][newpos.x] = self.id
            self.pos = newpos

        return can_move

