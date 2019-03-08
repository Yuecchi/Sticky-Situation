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

    def in_bounds(self, pos):
        if not pos.x >= 0 or not pos.x < len(game._game.level.tilemap.map[0]):
            return False
        elif not pos.y >= 0 or not pos.y < len(game._game.level.tilemap.map):
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
    # space for jump up
    JUMP_LEFT   = 10
    # space for jump down
    JUMP_RIGHT  = 12

class Player(Entity):

    ENTITY_TYPE = 1
    WALK_SPEED  = 1 / 32

    def __init__(self, pos, img):

        Entity.__init__(self, pos, img)
        game.entitymap[pos.y][pos.x] = self.id

        self.state = PlayerState.IDLE_RIGHT
        self.moving = False
        self.destination = None
        self.direction = Vector((1, 0))
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


        # TODO:  may need to change player move speed during state transition
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

        def jump_left(self):
            self.state = PlayerState.JUMP_LEFT
            self.sprite.set_animation(([0, 11], [4, 11]), 15)

        def jump_right(self):
            self.state = PlayerState.JUMP_RIGHT
            self.sprite.set_animation(([0, 12], [4, 12]), 15)

        states = {
            PlayerState.IDLE_UP    : idle_up,
            PlayerState.IDLE_LEFT  : idle_left,
            PlayerState.IDLE_DOWN  : idle_down,
            PlayerState.IDLE_RIGHT : idle_right,
            PlayerState.WALK_UP    : walk_up,
            PlayerState.WALK_LEFT  : walk_left,
            PlayerState.WALK_DOWN  : walk_down,
            PlayerState.WALK_RIGHT : walk_right,
            PlayerState.JUMP_LEFT  : jump_left,
            PlayerState.JUMP_RIGHT : jump_right
        }

        states[state](self)

    def check_current_tile(self, current_tile):

        def tile_empty(self):
            pass

        def tile_solid(self):
            pass # wtf?

        def tile_icy(self):
            self.moving = True
            self.go_idle()
            self.move(self.pos + self.direction)

        tiles = {
            TileType.EMPTY : tile_empty,
            TileType.SOLID : tile_solid,
            TileType.ICY   : tile_icy,
        }

        tiles[current_tile.type](self)


    def check_destination_tile(self, current_tile, destination_tile):

        def tile_empty(self, current_tile, destination_tile):
            return True

        def tile_solid(self, current_tile, destination_tile):
            return False

        def tile_icy(self, current_tile, destination_tile):
            return True

        # TODO: I still need to account for entities blocking the destination
        #  probably also need to account for over a fence into a fence (easy fix)
        def tile_left_fence(self, current_tile, destination_tile):
            # check if the player is moving from right to left
            if self.pos.x > self.destination.x:
                # check if the destination location isn't blocked
                jump_location = self.pos + Vector((-2, 0))
                jump_destination = tileEngine.get_tile(jump_location)
                if self.check_destination_tile(current_tile, jump_destination):
                    # change player destination and state
                    self.destination = jump_location
                    self.change_state(PlayerState.JUMP_LEFT)
                    return True
                else:
                    return False
            else:
                return False

        def tile_right_fence(self, current_tile, destination_tile):
            # check if the player is moving from right to left
            if self.pos.x < self.destination.x:
                # check if the destination location isn't blocked
                jump_location = self.pos + Vector((2, 0))
                jump_destination = tileEngine.get_tile(jump_location)
                if self.check_destination_tile(current_tile, jump_destination):
                    # change player destination and state
                    self.destination = jump_location
                    self.change_state(PlayerState.JUMP_RIGHT)
                    return True
                else:
                    return False
            else:
                return False

        tiles = {
            TileType.EMPTY       : tile_empty,
            TileType.SOLID       : tile_solid,
            TileType.ICY         : tile_icy,
            TileType.LEFT_FENCE  : tile_left_fence,
            TileType.RIGHT_FENCE : tile_right_fence
        }

        return tiles[destination_tile.type](self, current_tile, destination_tile,)

    def check_entity(self, entity):

        def push_block(self, entity):
            entity.direction = self.destination - self.pos
            return entity.move(entity.pos + entity.direction)

        entities = {
            PushBlock.ENTITY_TYPE : push_block
        }

        return entities[entity.ENTITY_TYPE](self, entity)

    def move(self, newpos):

        # set can move to true, so it is assumed that the player will be able to move
        can_move = True
        self.destination = newpos
        # check if the move is within the boundaries of the map
        if not self.in_bounds(self.destination):
            self.go_idle()
            return

        # check destination tile
        current_tile = tileEngine.get_tile(self.pos)
        destination_tile = tileEngine.get_tile(self.destination)
        can_move = self.check_destination_tile(current_tile, destination_tile)

        # check entity in destination tile
        entity = get_entity(self.destination)
        if entity:
            can_move = self.check_entity(entity)

        # if all checks are fine, move
        if can_move:
            self.moving = True
        else:
            self.go_idle()
            self.destination = None

    def go_idle(self):
        # TODO: may new to review this, but for now the model is sound
        if self.state >= 5 and self.state <= 8:
            self.change_state(self.state - 4)
        if self.state >= 9 and self.state <= 12:
            self.change_state(self.state - 8)

    def update_entitymap_pos(self):
        # move out of old location on entity map
        oldpos = self.pos - self.direction
        if game.entitymap[oldpos.y][oldpos.x] == Player.ENTITY_TYPE:
            game.entitymap[oldpos.y][oldpos.x] = 0
        # move into new location on entity map
        game.entitymap[self.pos.y][self.pos.x] = self.id

    def update(self):

        # check current location
        if not self.moving:
            current_tile = tileEngine.get_tile(self.pos)
            self.check_current_tile(current_tile)

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
                # if the player is not moving switch to an idle state
                # relative to the players current direction
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

def get_entity(pos):
    entity_id = game._game.level.entitymap[pos.y][pos.x]
    if bool(entity_id):
        return Entity.entities[entity_id - 1]
    else:
        return False