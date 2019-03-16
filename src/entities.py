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
        self.loop_animations = True

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
            if self.loop_animations:
                self.current_index = self.animation[0].copy()
            else:
                return
        else:
            self.current_index[0] = (self.current_index[0] + 1) % self.cols
            if self.current_index[0] == 0: self.current_index[1] += 1

class Entity:

    entities = []
    next_id = 1

    entity_updates = []
    entity_drawing = []
    entity_moveable = []


    def __init__(self, pos):

        # assign unique id to new entity and place it in the entity map
        self.id = Entity.next_id
        game._game.level.entitymap[pos.y][pos.x] = self.id

        Entity.next_id += 1
        self.pos = pos
        self.spawn = pos
        self.img = None
        self.sprite = None
        self.isTrigger = False
        self.isDoor = False

        self.dead = False
        self.dont_draw = False

        # add to list of entities
        Entity.entities.append(self)

    def in_bounds(self, pos):
        if not pos.x >= 0 or not pos.x < len(game._game.level.tilemap.map[0]):
            return False
        elif not pos.y >= 0 or not pos.y < len(game._game.level.tilemap.map):
            return False
        else:
            return True

    def check_destination(self):
        for entity in Entity.entity_moveable:
            if entity == self: continue
            if entity.moving:
                if self.destination == entity.destination:
                    self.destination -= self.direction
                    self.direction *= -1
                    return False
        return True

    def reset(self):
        pass

    def trigger(self):
        pass

    def update(self):
        pass

    def draw(self, canvas):
        if not self.dont_draw:
            self.sprite.draw(canvas, self.pos)

    def save_data(self):
        string = str(self.ENTITY_TYPE) + "," + str(self.spawn).strip("()")
        return string

    def contact_data(self):
        if self.isTrigger:
            if self.contact:
                if self.ENTITY_TYPE == Button.ENTITY_TYPE:
                    string = str(self.id) + "," + str(self.contact.id) + "," + str(self.timer // 60)
                else:
                    string = str(self.id) + "," + str(self.contact.id)
                return string

    def display(self):
        return str(self.ENTITY_TYPE)

class PlayerState(IntEnum):

    IDLE_UP     = 0
    IDLE_LEFT   = 1
    IDLE_DOWN   = 2
    IDLE_RIGHT  = 3
    WALK_UP     = 4
    WALK_LEFT   = 5
    WALK_DOWN   = 6
    WALK_RIGHT  = 7
    # space for jump up
    JUMP_LEFT   = 9
    # space for jump down
    JUMP_RIGHT  = 11
    DEAD        = 12

class Player(Entity):

    ENTITY_TYPE = 1
    WALK_SPEED  = 1 / 32
    DEFAULT_STATE = PlayerState.IDLE_DOWN
    SPRITESHEET = simplegui._load_local_image('../assets/SS_Horse_1.1.png')

    def __init__(self, pos):

        Entity.__init__(self, pos)
        Entity.entity_moveable.append(self)
        self.img = Player.SPRITESHEET
        self.sprite = Sprite(self.img)

        self.state = Player.DEFAULT_STATE
        self.moving = False
        self.destination = self.pos
        self.direction = Vector((1, 0))
        self.speed = Player.WALK_SPEED
        self.distance = None

        self.respawn_timer = 3
        self.respawn_time  = 0

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
            self.distance = 1
            self.move(self.pos + self.direction)

        def walk_left(self):
            self.state = PlayerState.WALK_LEFT
            self.sprite.set_animation(([0, 4], [3, 4]), 15)
            self.direction = Vector((-1, 0))
            self.distance = 1
            self.move(self.pos + self.direction)

        def walk_down(self):
            self.state = PlayerState.WALK_DOWN
            self.sprite.set_animation(([0, 5], [3, 5]), 15)
            self.direction = Vector((0, 1))
            self.distance = 1
            self.move(self.pos + self.direction)

        def walk_right(self):
            self.state = PlayerState.WALK_RIGHT
            self.sprite.set_animation(([0, 6], [3, 6]), 15)
            self.direction = Vector((1, 0))
            self.distance = 1
            self.move(self.pos + self.direction)

        def jump_left(self):
            self.state = PlayerState.JUMP_LEFT
            self.sprite.set_animation(([0, 11], [4, 11]), 15)
            self.distance = 2

        def jump_right(self):
            self.state = PlayerState.JUMP_RIGHT
            self.sprite.set_animation(([0, 12], [4, 12]), 15)
            self.distance = 2

        def dead(self):
            self.state = PlayerState.DEAD

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
            PlayerState.JUMP_RIGHT : jump_right,
            PlayerState.DEAD       : dead
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
            self.distance = 1
            self.move(self.pos + self.direction)

        def tile_left_fence(self):
            pass

        def tile_right_fence(self):
            pass

        def tile_conveyor_up(self):
            self.moving = True
            self.change_state(PlayerState.IDLE_UP)
            self.direction = Vector((0, -1))
            self.distance = 1
            self.move(self.pos + self.direction)

        def tile_conveyor_left(self):
            self.moving = True
            self.change_state(PlayerState.IDLE_LEFT)
            self.direction = Vector((-1, 0))
            self.distance = 1
            self.move(self.pos + self.direction)

        def tile_conveyor_down(self):
            self.moving = True
            self.change_state(PlayerState.IDLE_DOWN)
            self.direction = Vector((0, 1))
            self.distance = 1
            self.move(self.pos + self.direction)

        def tile_conveyor_right(self):
            self.moving = True
            self.change_state(PlayerState.IDLE_RIGHT)
            self.direction = Vector((1, 0))
            self.distance = 1
            self.move(self.pos + self.direction)

        def tile_spikes(self):
            self.kill()

        def tile_open_pit(self):
            self.kill()

        def tile_closed_pit(self):
            return True

        def tile_glue(self):
            self.kill()

        tiles = {
            TileType.EMPTY          : tile_empty,
            TileType.SOLID          : tile_solid,
            TileType.ICY            : tile_icy,
            TileType.LEFT_FENCE     : tile_left_fence,
            TileType.RIGHT_FENCE    : tile_right_fence,
            TileType.CONVEYOR_UP    : tile_conveyor_up,
            TileType.CONVEYOR_LEFT  : tile_conveyor_left,
            TileType.CONVEYOR_DOWN  : tile_conveyor_down,
            TileType.CONVEYOR_RIGHT : tile_conveyor_right,
            TileType.SPIKES         : tile_spikes,
            TileType.OPEN_PIT       : tile_open_pit,
            TileType.CLOSED_PIT     : tile_closed_pit,
            TileType.GLUE           : tile_glue
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

        def tile_conveyor_up(self, current_tile, destination_tile):
            if self.state == PlayerState.WALK_DOWN:
                return False
            return True

        def tile_conveyor_left(self, current_tile, destination_tile):
            if self.state == PlayerState.WALK_RIGHT:
                return False
            return True

        def tile_conveyor_down(self, current_tile, destination_tile):
            if self.state == PlayerState.WALK_UP:
                return False
            return True

        def tile_conveyor_right(self, current_tile, destination_tile):
            if self.state == PlayerState.WALK_LEFT:
                return False
            return True

        def tile_spikes(self, current_tile, destination_tile):
            return True

        def tile_open_pit(self, current_tile, destination_tile):
            return True

        def tile_closed_pit(self, current_tile, destination_tile):
            return True

        def tile_glue(self, current_tile, destination_tile):
            return True

        tiles = {
            TileType.EMPTY          : tile_empty,
            TileType.SOLID          : tile_solid,
            TileType.ICY            : tile_icy,
            TileType.LEFT_FENCE     : tile_left_fence,
            TileType.RIGHT_FENCE    : tile_right_fence,
            TileType.CONVEYOR_UP    : tile_conveyor_up,
            TileType.CONVEYOR_LEFT  : tile_conveyor_left,
            TileType.CONVEYOR_DOWN  : tile_conveyor_down,
            TileType.CONVEYOR_RIGHT : tile_conveyor_right,
            TileType.SPIKES         : tile_spikes,
            TileType.OPEN_PIT       : tile_open_pit,
            TileType.CLOSED_PIT     : tile_closed_pit,
            TileType.GLUE           : tile_glue
        }

        return tiles[destination_tile.type](self, current_tile, destination_tile,)

    def check_entity(self, entity): # player check entity method

        def player(self, entity):
            return True

        def push_block(self, entity):
            if entity.moving:
                return False
            else:
                entity.direction = self.direction
                return entity.move(entity.pos + entity.direction)

        def lever(self, entity):
            return False

        def button(self, entity):
            return False

        def panel(self, entity):
            entity.switch()
            return True

        def loose_panel(self, entity):
            entity.switch()
            game._game.level.entitymap[entity.pos.y][entity.pos.x] = self.id
            return True

        def vertical_door(self, entity):
            return entity.open

        def horizontal_door(self, entity):
            return entity.open

        def vertical_timed_door(self, entity):
            return entity.open

        def horizontal_timed_door(self, entity):
            return entity.open

        def scientist(self, entity):
            # TODO: may want to improve collision detection on scientists
            self.kill()

        entities = {
            Player.ENTITY_TYPE              : player,
            PushBlock.ENTITY_TYPE           : push_block,
            Lever.ENTITY_TYPE               : lever,
            Button.ENTITY_TYPE              : button,
            Panel.ENTITY_TYPE               : panel,
            LoosePanel.ENTITY_TYPE          : loose_panel,
            VerticalDoor.ENTITY_TYPE        : vertical_door,
            HorizontalDoor.ENTITY_TYPE      : horizontal_door,
            VerticalTimedDoor.ENTITY_TYPE   : vertical_timed_door,
            HorizontalTimedDoor.ENTITY_TYPE : horizontal_timed_door,
            Scientist.ENTITY_TYPE           : scientist
        }

        return entities[entity.ENTITY_TYPE](self, entity)

    def check_trigger(self, entity):

        if not entity.isTrigger:
            return

        def lever(self, entity):
            entity.switch()

        def button(self, entity):
            entity.switch()

        def panel(self, entity):
            pass

        def loose_panel(self, entity):
            pass

        triggers = {
            Lever.ENTITY_TYPE      : lever,
            Button.ENTITY_TYPE     : button,
            Panel.ENTITY_TYPE      : panel,
            LoosePanel.ENTITY_TYPE : loose_panel
        }

        triggers[entity.ENTITY_TYPE](self, entity)

    def move(self, newpos): # player move method

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
            self.destination = self.pos

    def go_idle(self):
        # TODO: may new to review this, but for now the model is sound
        if not self.dead:
            self.change_state(self.state % 4)

    def update_entitymap_pos(self):
        # move out of old location on entity map
        oldpos = self.pos - (self.direction * self.distance)
        if game._game.level.entitymap[oldpos.y][oldpos.x] == self.id:
            game._game.level.entitymap[oldpos.y][oldpos.x] = 0
            self.distance = None
        # move into new location on entity map
        game._game.level.entitymap[self.pos.y][self.pos.x] = self.id

    def kill(self):
        if not self.dead:
            # set dead flag to true
            self.dead = True
            # remove from entity map
            unmap_entity(self)
            # set animation looping to false
            self.sprite.loop_animations = False
            # play death animation (urgh)
            last_state = self.state % 4
            self.change_state(PlayerState.DEAD)

            if last_state == PlayerState.IDLE_UP:
                self.sprite.set_animation(([0, 7], [3, 7]), 10)
            elif last_state == PlayerState.IDLE_LEFT:
                self.sprite.set_animation(([0, 8], [3, 8]), 10)
            elif last_state == PlayerState.IDLE_DOWN:
                self.sprite.set_animation(([0, 9], [3, 9]), 10)
            elif last_state == PlayerState.IDLE_RIGHT:
                self.sprite.set_animation(([0, 10], [3, 10]), 10)

            # set respawn time
            self.respawn_time = self.respawn_timer * 60

    def respawn(self):
        self.dead = False
        self.change_state(Player.DEFAULT_STATE)
        game._game.level.reset_level()
        self.pos = self.spawn
        map_entity(self)

    def update(self): # player update method

        # check current location
        if not self.moving:
            current_tile = tileEngine.get_tile(self.pos)
            self.check_current_tile(current_tile)

        if not self.dead:
            # check if the player is already moving or not
            if not self.moving:

                # action button
                if handlers.keyboard.m:
                    trigger_location = self.pos + self.direction
                    entity = get_entity(trigger_location)
                    if entity:
                        self.check_trigger(entity)

                    handlers.keyboard.m = False

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
                    self.destination = self.pos
        else:

            if self.respawn_time > 0:
                self.respawn_time -= 1
            else:
                self.respawn()

class PushBlock(Entity):

    ENTITY_TYPE = 2
    SPRITESHEET = simplegui._load_local_image('../assets/testblock.png')

    def __init__(self, pos):

        Entity.__init__(self, pos)
        Entity.entity_moveable.append(self)
        self.img = PushBlock.SPRITESHEET
        self.sprite = Sprite(self.img)

        self.moving = False
        self.destination = self.pos
        self.direction = None
        self.speed = Player.WALK_SPEED
        self.stuck = False

    def reset(self):
        self.pos = self.spawn
        self.dead = False
        self.dont_draw = False

        self.moving = False
        self.destination = self.pos
        self.direction = None

    def check_current_tile(self, current_tile):

        def tile_empty(self):
            pass

        def tile_solid(self):
            pass

        def tile_icy(self):
            self.moving = True
            self.move(self.pos + self.direction)

        def tile_left_fence(self):
            pass

        def tile_right_fence(self):
            pass

        def tile_conveyor_up(self):
            self.moving = True
            self.direction = Vector((0, -1))
            self.move(self.pos + self.direction)

        def tile_conveyor_left(self):
            self.moving = True
            self.direction = Vector((-1, 0))
            self.move(self.pos + self.direction)

        def tile_conveyor_down(self):
            self.moving = True
            self.direction = Vector((0, 1))
            self.move(self.pos + self.direction)

        def tile_conveyor_right(self):
            self.moving = True
            self.direction = Vector((1, 0))
            self.move(self.pos + self.direction)

        def tile_spikes(self):
            pass

        def tile_open_pit(self):
            tileEngine.close_pit(self.pos)
            unmap_entity(self)
            self.dont_draw = True

        def tile_closed_pit(self):
            pass

        def tile_glue(self):
            self.stuck = True
            pass

        tiles = {
            TileType.EMPTY          : tile_empty,
            TileType.SOLID          : tile_solid,
            TileType.ICY            : tile_icy,
            TileType.LEFT_FENCE     : tile_left_fence,
            TileType.RIGHT_FENCE    : tile_right_fence,
            TileType.CONVEYOR_UP    : tile_conveyor_up,
            TileType.CONVEYOR_LEFT  : tile_conveyor_left,
            TileType.CONVEYOR_DOWN  : tile_conveyor_down,
            TileType.CONVEYOR_RIGHT : tile_conveyor_right,
            TileType.SPIKES         : tile_spikes,
            TileType.OPEN_PIT       : tile_open_pit,
            TileType.CLOSED_PIT     : tile_closed_pit,
            TileType.GLUE           : tile_glue
        }

        tiles[current_tile.type](self)

    def check_destination_tile(self, current_tile, destination_tile):

        def tile_empty(self, current_tile, destination_tile):
            return True

        def tile_solid(self, current_tile, destination_tile):
            return False

        def tile_icy(self, current_tile, destination_tile):
            return True

        def tile_left_fence(self, current_tile, destination_tile):
            return False

        def tile_right_fence(self, current_tile, destination_tile):
            return False

        def tile_conveyor_up(self, current_tile, destination_tile):
            return True

        def tile_conveyor_left(self, current_tile, destination_tile):
            return True

        def tile_conveyor_down(self, current_tile, destination_tile):
            return True

        def tile_conveyor_right(self, current_tile, destination_tile):
            return True

        def tile_spikes(self, current_tile, destination_tile):
            return False

        def tile_open_pit(self, current_tile, destination_tile):
            return True

        def tile_closed_pit(self, current_tile, destination_tile):
            return True

        def tile_glue(self, current_tile, destination_tile):
            return True

        tiles = {
            TileType.EMPTY          : tile_empty,
            TileType.SOLID          : tile_solid,
            TileType.ICY            : tile_icy,
            TileType.LEFT_FENCE     : tile_left_fence,
            TileType.RIGHT_FENCE    : tile_right_fence,
            TileType.CONVEYOR_UP    : tile_conveyor_up,
            TileType.CONVEYOR_LEFT  : tile_conveyor_left,
            TileType.CONVEYOR_DOWN  : tile_conveyor_down,
            TileType.CONVEYOR_RIGHT : tile_conveyor_right,
            TileType.SPIKES         : tile_spikes,
            TileType.OPEN_PIT       : tile_open_pit,
            TileType.CLOSED_PIT     : tile_closed_pit,
            TileType.GLUE           : tile_glue
        }

        return tiles[destination_tile.type](self, current_tile, destination_tile,)

    def check_entity(self, entity): # push block check entity method

        def player(self, entity):
            return False

        def push_block(self, entity):
            return False

        def lever(self, entity):
            return False

        def button(self, entity):
            return False

        def panel(self, entity):
            entity.switch()
            return True

        def loose_panel(self, entity):
            entity.switch()
            game._game.level.entitymap[entity.pos.y][entity.pos.x] = self.id
            return True

        def vertical_door(self, entity):
            return entity.open

        def horizontal_door(self, entity):
            return entity.open

        def vertical_timed_door(self, entity):
            return entity.open

        def horizontal_timed_door(self, entity):
            return entity.open

        def scientist(self, entity):
            return False

        entities = {
            Player.ENTITY_TYPE               : player,
            PushBlock.ENTITY_TYPE            : push_block,
            Lever.ENTITY_TYPE                : lever,
            Button.ENTITY_TYPE               : button,
            Panel.ENTITY_TYPE                : panel,
            LoosePanel.ENTITY_TYPE           : loose_panel,
            VerticalDoor.ENTITY_TYPE         : vertical_door,
            HorizontalDoor.ENTITY_TYPE       : horizontal_door,
            VerticalTimedDoor.ENTITY_TYPE    : vertical_timed_door,
            HorizontalTimedDoor.ENTITY_TYPE  : horizontal_timed_door,
            Scientist.ENTITY_TYPE            : scientist
        }

        return entities[entity.ENTITY_TYPE](self, entity)

    def move(self, newpos): # push block move method

        if self.stuck:
            return False

        can_move = True
        self.destination = newpos

        # check if the move is within the boundaries of the map
        if not self.in_bounds(newpos):
            return False

        # check destination tile
        current_tile = tileEngine.get_tile(self.pos)
        destination_tile = tileEngine.get_tile(self.destination)
        can_move = self.check_destination_tile(current_tile, destination_tile)

        # check entity in destination tile
        entity = get_entity(self.destination)
        if entity:
            can_move = self.check_entity(entity)

        obstruction = self.check_destination()
        if not obstruction:
            can_move = obstruction

        # if all checks are fine, move
        if can_move:
            self.moving = True
        else:
            self.destination = self.pos

        return can_move

    def update_entitymap_pos(self):
        # move out of old location on entity map
        oldpos = self.pos - self.direction
        if game._game.level.entitymap[oldpos.y][oldpos.x] == self.id:
            game._game.level.entitymap[oldpos.y][oldpos.x] = 0
        # move into new location on entity map
        game._game.level.entitymap[self.pos.y][self.pos.x] = self.id

    def update(self): # push block update method

        # check current location
        if not self.moving:
            current_tile = tileEngine.get_tile(self.pos)
            self.check_current_tile(current_tile)

        if self.moving:
            self.check_destination()
            entity = get_entity(self.destination)
            if entity:
                pass
            if self.pos != self.destination:
                self.pos += (self.direction * self.speed)
            else:
                self.moving = False
                self.pos.to_int()
                self.update_entitymap_pos()
                self.destination = self.pos

class Trigger(Entity):

    def __init__(self, pos):
        Entity.__init__(self, pos)
        self.isTrigger = True

        self.on = False
        self.contacts = []
        self.contact = None

    def add_contact(self, contact):
        self.contacts.append(contact)

    def set_contact(self, contact):
        self.contact = contact



class Lever(Trigger):

    ENTITY_TYPE = 3
    SPRITESHEET = simplegui._load_local_image('../assets/lever.png')

    def __init__(self, pos):

        Trigger.__init__(self, pos)
        self.img = Lever.SPRITESHEET
        self.sprite = Sprite(self.img)

    def reset(self):

        self.pos = self.spawn
        self.dead = False

        self.on = False
        self.sprite.set_animation(([0, 0], [0, 0]), 1)

    def switch(self):
        # check if there are any existing contacts
        if len(self.contacts) != 0:

            triggered = []
            # attempt to trigger all contacts
            for contact in self.contacts:

                if contact.trigger():
                    # store each contact which has successfully triggered
                    triggered.append(contact)
                else:
                    # if a contact does not trigger, reset all triggered contacts
                    for trigger in triggered:
                        trigger.trigger()
                    return

            # if all contacts sucessfully triggered, fltip the switch
            self.on = not self.on

            if self.on:
                self.sprite.set_animation(([1, 0], [1, 0]), 1)
            else:
                self.sprite.set_animation(([0, 0], [0, 0]), 1)

class Button(Trigger):

    ENTITY_TYPE = 4
    SPRITESHEET = simplegui._load_local_image('../assets/button.png')

    def  __init__(self, pos):

        Trigger.__init__(self, pos)
        self.img = Button.SPRITESHEET
        self.sprite = Sprite(self.img)

        self.timer = 0
        self.time  = 0

    def reset(self):
        self.pos = self.spawn
        self.dead = False

        self.on = False

        self.time = 0
        self.sprite.set_animation(([0, 0], [0, 0]), 1)

    # set the number of second the timer will count down from
    def set_timer(self, timer):
        self.timer = timer * 60

    def switch(self):

        if self.contact:

            if self.contact.trigger():
                self.on = not self.on

                if self.on:
                    self.time = self.timer
                    self.sprite.set_animation(([1, 0], [1, 0]), 1)
                else:
                    self.time = 0
                    self.sprite.set_animation(([0, 0], [0, 0]), 1)

    def update(self):

        # check timer
        if self.on:
            if self.time > 0:
                self.time -= 1
            if self.time == 0:
                self.switch()


class Panel(Trigger):

    ENTITY_TYPE = 5
    SPRITESHEET = simplegui._load_local_image('../assets/panel.png')

    def __init__(self, pos):

        Trigger.__init__(self, pos)
        self.img = Panel.SPRITESHEET
        self.sprite = Sprite(self.img)

    def reset(self):
        self.pos = self.spawn
        self.dead = False

        self.on = False
        self.sprite.set_animation(([0, 0], [0, 0]), 1)


    def switch(self):

        if self.contact:

            if self.contact.trigger():
                self.on = not self.on

                if self.on:
                    unmap_entity(self)
                    self.sprite.set_animation(([1, 0], [1, 0]), 1)
                else:
                    map_entity(self)
                    self.sprite.set_animation(([0, 0], [0, 0]), 1)

    def trigger(self):

        if not self.on:
            return False
        else:
            # check for obstructions
            entity = get_entity(self.pos)
            if entity:
                if entity.ENTITY_TYPE != self.ENTITY_TYPE:
                    return False

            self.switch()
            return True

class LoosePanel(Trigger):

    ENTITY_TYPE = 6
    SPRITESHEET = simplegui._load_local_image('../assets/loose_panel.png')

    def __init__(self, pos):

        Trigger.__init__(self, pos)
        self.img = LoosePanel.SPRITESHEET
        self.sprite = Sprite(self.img)

    def reset(self):
        self.pos = self.spawn
        self.dead = False

        self.on = False
        self.sprite.set_animation(([0, 0], [0, 0]), 1)

    def switch(self):

        if self.contact:

            if self.contact.trigger():

                self.on = not self.on

                if self.on:
                    unmap_entity(self)
                    self.sprite.set_animation(([1, 0], [1, 0]), 1)
                else:
                    map_entity(self)
                    self.sprite.set_animation(([0, 0], [0, 0]), 1)

    def update(self):

        if self.on:
            # check if there is anything keeping it pressed down
            if not get_entity(self.pos):
                self.switch()

#TODO: probably makes sense to make an ecompassing door class at this point

class Door(Entity):

    def __init__(self, pos):

        Entity.__init__(self, pos)
        self.isDoor = True

        self.open = False

    def reset(self):
        self.pos = self.spawn
        self.dead = False

        self.open = False
        self.sprite.set_animation(([0, 0], [0, 0]), 1)

    def trigger(self):

        #check for obstructions
        entity = get_entity(self.pos)
        if entity:
            if entity.ENTITY_TYPE != self.ENTITY_TYPE:
                return False

        #TODO: do an entity destination check here

        self.open = not self.open

        if self.open:
            unmap_entity(self)
            self.sprite.set_animation(([1, 0], [1, 0]), 1)
        else:
            map_entity(self)
            self.sprite.set_animation(([0, 0], [0, 0]), 1)

        return True

class VerticalDoor(Door):

    ENTITY_TYPE = 7
    SPRITESHEET = simplegui._load_local_image('../assets/vert_door.png')

    def __init__(self, pos):

        Door.__init__(self, pos)
        self.img = VerticalDoor.SPRITESHEET
        self.sprite = Sprite(self.img)

        self.open = False

class HorizontalDoor(Door):

    ENTITY_TYPE = 8
    SPRITESHEET = simplegui._load_local_image('../assets/hori_door.png')

    def __init__(self, pos):

        Door.__init__(self, pos)
        self.img = HorizontalDoor.SPRITESHEET
        self.sprite = Sprite(self.img)

        self.open = False

class VerticalTimedDoor(Door):

    ENTITY_TYPE = 9
    SPRITESHEET = simplegui._load_local_image("../assets/vert_timed_door.png")

    def __init__(self, pos):

        Door.__init__(self, pos)
        self.img = VerticalTimedDoor.SPRITESHEET
        self.sprite= Sprite(self.img)

        self.open = False
        self.timer = 0
        self.time = 0

    def set_timer(self, timer):
        self.timer = timer * 60

    def trigger(self):

        # if the door is closed, open it
        if not self.open:
            self.open = True
            unmap_entity(self)
            self.sprite.set_animation(([1, 0], [1, 0]), 1)


        # restart the timer
        self.time = self.timer
        return True

    def update(self):

        if self.open:
            if self.time > 0:
                self.time -= 1
            else:
                # check for obstructions
                entity = get_entity(self.pos)
                if entity:
                    if entity.ENTITY_TYPE != self.ENTITY_TYPE:
                        return

                # TODO: do an entity destination check here

                # if no obstuctions are found, close the door
                self.open = False
                map_entity(self)
                self.sprite.set_animation(([0, 0], [0, 0]), 1)

class HorizontalTimedDoor(Door):

    ENTITY_TYPE = 10
    SPRITESHEET = simplegui._load_local_image("../assets/hori_timed_door.png")

    def __init__(self, pos):

        Door.__init__(self, pos)
        self.img = HorizontalTimedDoor.SPRITESHEET
        self.sprite= Sprite(self.img)

        self.open = False
        self.timer = 0
        self.time = 0

    def set_timer(self, timer):
        self.timer = timer * 60

    def trigger(self):

        # if the door is closed, open it
        if not self.open:
            self.open = True
            unmap_entity(self)
            self.sprite.set_animation(([1, 0], [1, 0]), 1)


        # restart the timer
        self.time = self.timer
        return True

    def update(self):

        if self.open:
            if self.time > 0:
                self.time -= 1
            else:
                # check for obstructions
                entity = get_entity(self.pos)
                if entity:
                    if entity.ENTITY_TYPE != self.ENTITY_TYPE:
                        return

                # TODO: do an entity destination check here

                # if no obstuctions are found, close the door
                self.open = False
                map_entity(self)
                self.sprite.set_animation(([0, 0], [0, 0]), 1)


class ScientistState(IntEnum):

    WALK_UP    = 1
    WALK_LEFT  = 2
    WALK_DOWN  = 3
    WALK_RIGHT = 4

class Scientist(Entity):

    ENTITY_TYPE = 11
    SPRITESHEET = simplegui._load_local_image("../assets/scientist.png")
    WALK_SPEED  = 1 / 64

    def __init__(self, pos):

        Entity.__init__(self, pos)
        Entity.entity_moveable.append(self)
        self.img = Scientist.SPRITESHEET
        self.sprite = Sprite(self.img)

        self.patrol_point = Vector()

        self.state = None
        self.moving = False
        self.destination = Vector()
        self.direction = Vector()
        self.speed = Scientist.WALK_SPEED

    def set_patrol(self, patrol):
        self.patrol = patrol
        direction = (self.patrol - self.pos).normalize()

        if direction == Vector((0, -1)):
            self.change_state(ScientistState.WALK_UP)
        elif direction == Vector((-1, 0)):
            self.change_state(ScientistState.WALK_LEFT)
        elif direction == Vector((0, 1)):
            self.change_state(ScientistState.WALK_DOWN)
        elif direction == Vector((1, 0)):
            self.change_state(ScientistState.WALK_RIGHT)

    def change_direction(self):
        direction = self.direction * -1

        if direction == Vector((0, -1)):
            self.change_state(ScientistState.WALK_UP)
        elif direction == Vector((-1, 0)):
            self.change_state(ScientistState.WALK_LEFT)
        elif direction == Vector((0, 1)):
            self.change_state(ScientistState.WALK_DOWN)
        elif direction == Vector((1, 0)):
            self.change_state(ScientistState.WALK_RIGHT)

    def change_state(self, state):

        def walk_up(self):
            self.direction = Vector((0, -1))
            self.sprite.set_animation(([0, 3], [3, 3]), 15)
            self.move(self.pos + self.direction)

        def walk_left(self):
            self.direction = Vector((-1, 0))
            self.sprite.set_animation(([0, 1], [3, 1]), 15)
            self.move(self.pos + self.direction)

        def walk_down(self):
            self.direction = Vector((0, 1))
            self.sprite.set_animation(([0, 0], [3, 0]), 15)
            self.move(self.pos + self.direction)

        def walk_right(self):
            self.direction = Vector((1, 0))
            self.sprite.set_animation(([0, 2], [3, 2]), 15)
            self.move(self.pos + self.direction)

        states = {

            ScientistState.WALK_UP    : walk_up,
            ScientistState.WALK_LEFT  : walk_left,
            ScientistState.WALK_DOWN  : walk_down,
            ScientistState.WALK_RIGHT : walk_right

        }

        states[state](self)

    def check_entity(self, entity): # player check entity method

        def player(self, entity):
            entity.kill()
            return True

        def push_block(self, entity):
            self.change_direction()
            return True

        def lever(self, entity):
            self.change_direction()
            return True

        def button(self, entity):
            self.change_direction()
            return True

        def panel(self, entity):
            self.change_direction()
            return True

        def loose_panel(self, entity):
            self.change_direction()
            return True

        def vertical_door(self, entity):
            if not entity.open:
                self.change_direction()
            return True

        def horizontal_door(self, entity):
            if not entity.open:
                self.change_direction()
            return True

        def vertical_timed_door(self, entity):
            if not entity.open:
                self.change_direction()
            return True

        def horizontal_timed_door(self, entity):
            if not entity.open:
                self.change_direction()
            return True

        def scientist(self, entity):
            self.change_direction()
            return True

        entities = {
            Player.ENTITY_TYPE              : player,
            PushBlock.ENTITY_TYPE           : push_block,
            Lever.ENTITY_TYPE               : lever,
            Button.ENTITY_TYPE              : button,
            Panel.ENTITY_TYPE               : panel,
            LoosePanel.ENTITY_TYPE          : loose_panel,
            VerticalDoor.ENTITY_TYPE        : vertical_door,
            HorizontalDoor.ENTITY_TYPE      : horizontal_door,
            VerticalTimedDoor.ENTITY_TYPE   : vertical_timed_door,
            HorizontalTimedDoor.ENTITY_TYPE : horizontal_timed_door,
            Scientist.ENTITY_TYPE           : scientist
        }

        return entities[entity.ENTITY_TYPE](self, entity)

    def reset(self):
        self.pos = self.spawn
        self.set_patrol(self.patrol)

    def move(self, newpos): #scientist move
        can_move = True
        self.destination = newpos
        # check if the move is within the boundaries of the map
        if not self.in_bounds(self.destination):
            self.destination = self.pos
            return
        # check destination tile
        entity = get_entity(self.destination)
        if entity:
            can_move = self.check_entity(entity)

        # if all checks are fine, move
        if can_move:
            self.moving = True
        else:
            self.moving = False # probably?
            self.destination = self.pos

    def update_entitymap_pos(self):
        # move out of old location on entity map
        oldpos = self.pos - self.direction
        if game._game.level.entitymap[oldpos.y][oldpos.x] == self.id:
            game._game.level.entitymap[oldpos.y][oldpos.x] = 0
            self.distance = None
        # move into new location on entity map
        game._game.level.entitymap[self.pos.y][self.pos.x] = self.id

    def update(self):

        if self.moving:
            if self.pos != self.destination:
                self.pos += (self.direction * self.speed)
            else:
                self.pos.to_int()
                self.update_entitymap_pos()

                if self.pos == self.patrol:
                    self.change_direction()
                elif self.pos == self.spawn:
                    self.change_direction()
                else:
                    self.move(self.pos + self.direction)

def get_entity(pos):
    entity_id = game._game.level.entitymap[pos.y][pos.x]
    if bool(entity_id):
        return Entity.entities[entity_id - 1]
    else:
        return False

def map_entity(entity):
    game._game.level.entitymap[entity.pos.y][entity.pos.x] = entity.id

def unmap_entity(entity):
    game._game.level.entitymap[entity.pos.y][entity.pos.x] = 0
