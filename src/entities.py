try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from enum import IntEnum

import game
import handlers

from vectors import Vector
import tileEngine
from tileEngine import TileType

TILESIZE = tileEngine.TILESIZE
HALFSIZE = tileEngine.HALFSIZE
TILE_DIMS = tileEngine.TILE_DIMS

class Sprite:

    def __init__(self, img):
        self.img = img
        self.cols = self.img.get_width() / TILESIZE

        self.animation = ([0, 0], [0, 0])
        self.animation_speed = 1
        self.current_index = self.animation[0].copy()

    def set_animation(self, animation, speed):
        self.animation = animation
        self.current_index = self.animation[0].copy()
        self.animation_speed = speed

    def set_animation_speed(self, speed):
        self.animation_speed = speed

    def draw(self, canvas, map_pos):
        scroll =  game._game.camera.pos
        pos = (HALFSIZE + ((map_pos.x - scroll.x) * TILESIZE), HALFSIZE + ((map_pos.y - scroll.y) * TILESIZE))
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

    def in_bounds(self, newpos):
        if not newpos.x >= 0 or not newpos.x < len(game._game.level.tilemap.map[0]):
            return False
        elif not newpos.y >= 0 or not newpos.y < len(game._game.level.tilemap.map):
            return False
        else:
            return True


    def draw(self, canvas):
        self.sprite.draw(canvas, self.pos)


class PlayerState(IntEnum):

    IDLE_UP     = 1
    IDLE_LEFT   = 2
    IDLE_DOWN   = 3
    IDLE_RIGHT  = 4
    WALK_UP     = 5
    WALK_LEFT   = 6
    WALK_DOWN   = 7
    WALK_RIGHT  = 8

class Player(Entity):

    ENTITY_TYPE = 1
    WALK_SPEED  = 1 / 32

    def __init__(self, pos, img):

        Entity.__init__(self, pos, img)
        game.entitymap[pos.y][pos.x] = self.id

        self.state = PlayerState.IDLE_RIGHT
        self.moving = False
        self.destination = None
        self.direction = None
        self.speed = Player.WALK_SPEED

    def change_state(self, state):

        def idle_up(self):
            self.state = PlayerState.IDLE_UP
            self.sprite.set_animation(([0, 2], [0, 2]), 1)

        def idle_left(self):
            self.state = PlayerState.IDLE_LEFT
            self.sprite.set_animation(([1, 2], [1, 2]), 1)

        def idle_down(self):
            self.state = PlayerState.IDLE_DOWN
            self.sprite.set_animation(([2, 2], [2, 2]), 1)

        def idle_right(self):
            self.state = PlayerState.IDLE_RIGHT
            self.sprite.set_animation(([3, 2], [3, 2]), 1)

        def walk_up(self):
            self.state = PlayerState.WALK_UP
            self.sprite.set_animation(([0, 3], [3, 3]), 15)
            self.direction = Vector((0, -1))
            self.move(self.pos + self.direction)

        def walk_left(self):
            self.state = PlayerState.WALK_LEFT
            self.sprite.set_animation(([0, 4], [3, 4]), 15)
            self.direction = Vector((-1, 0))
            self.move(self.pos + self.direction)

        def walk_down(self):
            self.state = PlayerState.WALK_DOWN
            self.sprite.set_animation(([0, 5], [3, 5]), 15)
            self.direction = Vector((0, 1))
            self.move(self.pos + self.direction)

        def walk_right(self):
            self.state = PlayerState.WALK_RIGHT
            self.sprite.set_animation(([0, 6], [3, 6]), 15)
            self.direction = Vector((1, 0))
            self.move(self.pos + self.direction)

        states = {
            1 : idle_up,
            2 : idle_left,
            3 : idle_down,
            4 : idle_right,
            5 : walk_up,
            6 : walk_left,
            7 : walk_down,
            8 : walk_right
        }

        states[state](self)

    def move(self, newpos):

        # set can move to true, so it is assumed that the player will be able to move
        can_move = True
        # check if the move is within the boundaries of the map
        if not self.in_bounds(newpos):
            self.go_idle()
            return

        #TODO: check tile at self.pos?

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
                entity.direction = newpos - self.pos
                can_move = entity.move(entity.pos + entity.direction)

        # TODO: movement will likely require a more complex algorithm than this
        # if all checks are fine, move
        if can_move:
            self.moving = True
            self.destination =  newpos
        else:
            self.go_idle()

    def go_idle(self):
        # TODO: may need to account for states other than walk states
        self.change_state(self.state - 4)

    def update_entitymap_pos(self):
        # move out of old location on entity map
        oldpos = self.pos - self.direction
        if game.entitymap[oldpos.y][oldpos.x] == Player.ENTITY_TYPE:
            game.entitymap[oldpos.y][oldpos.x] = 0
        # move into new location on entity map
        game.entitymap[self.pos.y][self.pos.x] = self.id

    def update(self):

        # check if the player is already moving or not
        if not self.moving:
            # change player states based on keyboard input
            if handlers.keyboard.w:
                self.change_state(PlayerState.WALK_UP)
            elif handlers.keyboard.a:
                self.change_state(PlayerState.WALK_LEFT)
            elif handlers.keyboard.s:
                self.change_state(PlayerState.WALK_DOWN)
            elif handlers.keyboard.d:
                self.change_state(PlayerState.WALK_RIGHT)
            else:
                # if the player is not moving but in a walking state
                # switch to an idle state which faces the same direction
                if self.state >= 5 and self.state <= 8:
                    self.go_idle()
        else:
            # keep moving towards the destination until is has been reached
            if self.pos != self.destination:
                self.pos += (self.direction * self.speed)
            else:
                self.moving = False
                self.pos.to_int()
                self.update_entitymap_pos()
                self.destination = None
                self.direction = None

class PushBlock(Entity):

    ENTITY_TYPE = 2

    def __init__(self, pos, img):

        Entity.__init__(self, pos, img)

        # place new entity into the entity map
        game.entitymap[pos.y][pos.x] = self.id

        self.moving = False
        self.destination = None
        self.direction = None
        self.speed = Player.WALK_SPEED

    def move(self, newpos):

        can_move = True

        # check if the move is within the boundaries of the map
        if not self.in_bounds(newpos): return False

        # check tile at newpos
        tile_index = game.tilemap.map[newpos.y][newpos.x]
        tile = game.tilemap.tilesheet.tiles[tile_index]
        if tile.type == TileType.SOLID:
            can_move = False
        # if all checks are fine, move
        if can_move:
            self.moving = True
            self.destination = newpos

        return can_move

    def update_entitymap_pos(self):
        # move into new location on entity map
        game.entitymap[self.pos.y][self.pos.x] = self.id

    def update(self):
        if self.moving:
            if self.pos != self.destination:
                self.pos = self.pos + (self.direction * self.speed)
            else:
                self.moving = False
                self.pos.to_int()
                self.update_entitymap_pos()
                self.destination = None
                self.direction = None

