try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import game
from tileEngine import TileType
from enum import IntEnum

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

        if game._game.clock.transition(self.animation_speed): self.next_frame()

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


class PlayerState(IntEnum):

    UP    = 1
    LEFT  = 2
    DOWN  = 3
    RIGHT = 4

class Player(Entity):

    ENTITY_TYPE = 1

    def __init__(self, pos, img):

        Entity.__init__(self, pos, img)
        game.entitymap[pos.y][pos.x] = self.id

    def move(self, newpos):

        # set can move to true, so it is assumed that the player will be able to move
        can_move = True

        # check if the move is within the boundaries of the map
        if not newpos.x >= 0 or not newpos.x < len(game._game.level.tilemap.map[0]):
            return
        if not newpos.y >= 0 or not newpos.y < len(game._game.level.tilemap.map):
            return

        # check tile at self.pos?

        # check tile at newpos
        tile_index = game.tilemap.map[newpos.y][newpos.x]
        tile = game.tilemap.tilesheet.tiles[tile_index]
        if tile.type == TileType.SOLID:
            can_move = False
        # TODO: if ice, move in direction until not ice

        # check entity at newpos
        entity_id = game.entitymap[newpos.y][newpos.x]
        if bool(entity_id):
            entity = Entity.entities[entity_id - 1]
            if entity.ENTITY_TYPE == PushBlock.ENTITY_TYPE:
                pushpos = newpos - self.pos
                can_move = entity.move(entity.pos + pushpos)


        # TODO: movement will likely require a more complex algorithm than this
        # if all checks are fine, move
        if can_move:
            game.entitymap[self.pos.y][self.pos.x] = 0
            game.entitymap[newpos.y][newpos.x] = self.id
            self.pos = newpos

class PushBlock(Entity):

    ENTITY_TYPE = 2

    def __init__(self, pos, img):

        Entity.__init__(self, pos, img)

        game.entitymap[pos.y][pos.x] = self.id

    def move(self, newpos):

        can_move = True

        # check if the move is within the boundaries of the map
        if not newpos.x >= 0 or not newpos.x < len(game._game.level.tilemap.map[0]):
            return False
        if not newpos.y >= 0 or not newpos.y < len(game._game.level.tilemap.map):
            return False

        # check tile at newpos
        tile_index = game.tilemap.map[newpos.y][newpos.x]
        tile = game.tilemap.tilesheet.tiles[tile_index]
        if tile.type == TileType.SOLID:
            can_move = False
        # if all checks are fine, move
        if can_move:
            game.entitymap[self.pos.y][self.pos.x] = 0
            game.entitymap[newpos.y][newpos.x] = self.id
            self.pos = newpos

        return can_move

