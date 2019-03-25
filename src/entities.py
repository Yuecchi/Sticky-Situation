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
import math
from random import randint

TILESIZE = tileEngine.TILESIZE
HALFSIZE = tileEngine.HALFSIZE
TILE_DIMS = tileEngine.TILE_DIMS

# the sprite class handles all drawing of in game entities and animated
# images which are not tiles
class Sprite:

    def __init__(self, img):

        # sources image and dimensions
        self.img = img
        self.cols = self.img.get_width() / TILESIZE

        self.animation = ([0, 0], [0, 0]) # stores the current set of animation frames to be looped over
        self.animation_speed = 1 # stores the current animation speed
        self.current_index = self.animation[0].copy() # stores the current animation frame to be drawn
        # determines whether or not the current set of animation frames will be looped over
        # or cycled through a single time
        self.loop_animations = True

    # sets the current set of animation frames and the animation speed
    def set_animation(self, animation, speed):
        self.animation = animation
        self.current_index = self.animation[0].copy()
        self.animation_speed = speed

    # set the animation speed
    def set_animation_speed(self, speed):
        self.animation_speed = speed

    # draws the sprite
    def draw(self, canvas, map_pos):
        # grabs the cameras current location
        scroll =  game._game.camera.pos
        # determines where to draw the sprite on the canvas
        pos = (HALFSIZE + ((map_pos.x - scroll.x) * TILESIZE), HALFSIZE + ((map_pos.y - scroll.y) * TILESIZE))
        # determines which animation frame to draw
        src_pos = (HALFSIZE + (self.current_index[0] * TILESIZE), HALFSIZE + (self.current_index[1] * TILESIZE))
        canvas.draw_image(self.img, src_pos, TILE_DIMS, pos, TILE_DIMS)

        # cycles through an animations frames
        if game._game.clock.transition(self.animation_speed): self.next_frame()

    # special draw method for drawing rotating sprites. works the same, but allows for rotation
    def rot_draw(self, canvas, map_pos, angle):
        scroll =  game._game.camera.pos
        pos = (HALFSIZE + ((map_pos.x - scroll.x) * TILESIZE), HALFSIZE + ((map_pos.y - scroll.y) * TILESIZE))
        src_pos = (HALFSIZE + (self.current_index[0] * TILESIZE), HALFSIZE + (self.current_index[1] * TILESIZE))
        canvas.draw_image(self.img, src_pos, TILE_DIMS, pos, TILE_DIMS, angle)

        if game._game.clock.transition(self.animation_speed): self.next_frame()

    # determines the sprites next animation frame
    def next_frame(self):
        if self.current_index == self.animation[1]:
            if self.loop_animations:
                self.current_index = self.animation[0].copy()
            else:
                return
        else:
            self.current_index[0] = (self.current_index[0] + 1) % self.cols
            if self.current_index[0] == 0: self.current_index[1] += 1

# The super class Entity is responsible for all in game objects which aren't tiles and projectiles
# so this includes doors, triggers and anything which moves (player, pushblock etc) besides projectiles
# The entity class contains all the basic data attributes and methods which all entities should has, such as
# a position vector and a draw / update method
class Entity:

    # stores all entities in the current level. This allows
    # entities to be referenced by an index which is assigned to them
    # upon creating, and accessed via the entity map
    entities = []
    next_id = 1 # stores the id of the next entity to be created

    # rearranged lists of entities for various purposes, for example the
    # order in which entities are updated, is different to the order in which
    # they are drawn. A list of moveable entities is also stored to make
    # certain checks faster
    entity_updates = []
    entity_drawing = []
    entity_moveable = []

    def __init__(self, pos):

        # assign unique id to new entity and place it in the entity map
        self.id = Entity.next_id
        game._game.level.entitymap[pos.y][pos.x] = self.id
        Entity.next_id += 1

        self.pos = pos # position vector of an entitiy, which is a grid reference
        self.spawn = pos # the spawn location of an entitiy. This is where the entity resets on player death
        self.img = None # the source image for an entitiy
        self.sprite = None # the sprite obbject of an entity, enabling drawing an animations of the entity
        self.isTrigger = False # true when an entity is also a trigger
        self.isDoor = False # true when an entity is also a door

        self.dead = False # keep track of whether or not an entity is dead or alive
        self.dont_draw = False # keeps track of whether or not an entity needs to be drawn

        # add to list of entities
        Entity.entities.append(self)

    # method used to check if a given position is within the confines of the current
    # games tile map (the playable area)
    def in_bounds(self, pos):
        if not pos.x >= 0 or not pos.x < len(game._game.level.tilemap.map[0]):
            return False
        elif not pos.y >= 0 or not pos.y < len(game._game.level.tilemap.map):
            return False
        else:
            return True

    # cross checks the destinations of moveable entities
    # this is done to detect if two enities are moving into the
    # same square at the same time
    def check_destination(self):
        for entity in Entity.entity_moveable:
            if entity == self: continue
            if entity.moving:
                # when detected, one of the two entities is sent back to where it was coming from
                if self.destination == entity.destination:
                    self.destination -= self.direction
                    self.direction *= -1
                    return False
        return True

    # empty method ( an idea which was never implemented)
    def reset(self):
        pass

    # empty method ( I believe this might actually be redundant?)
    def trigger(self):
        pass

    # empty method ( simplifies looping through entity update methods)
    def update(self):
        pass

    # a general draw method for all entities
    def draw(self, canvas):
        if not self.dont_draw:
            self.sprite.draw(canvas, self.pos)

    # a general method for storing entitiy data externally
    def save_data(self):
        string = str(self.ENTITY_TYPE) + "," + str(self.spawn).strip("()")
        return string

    def contact_data(self):
        pass

    # method used as a debug tool
    def display(self):
        return str(self.ENTITY_TYPE)

# list of player states, which determine how the player
# will move and be animated / if the player is alive or dead
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
    JUMP_DOWN   = 10
    JUMP_RIGHT  = 11
    DEAD        = 12

# list of player deaths which determine which
# death animation / sound to play
class PlayerDeath(IntEnum):

    SPIKE = 0
    GLUE  = 1
    FIRE  = 2
    FAN   = 3
    WATER = 4
    GHOST = 5

# the player class contains the all instance data for the player controlled entity (the horse)
class Player(Entity):

    ENTITY_TYPE = 1 # player entity type
    WALK_SPEED  = 1 / 32 # player movement speed
    DEFAULT_STATE = PlayerState.IDLE_DOWN
    SPRITESHEET = simplegui._load_local_image('../assets/entities/horse.png')

    JUMP_SOUND = simplegui._load_local_sound('../assets/entities/jump1.wav')

    SPIKE_DEATH_SOUND = simplegui._load_local_sound('../assets/entities/spike_death.wav')
    WATER_DEATH_SOUND = simplegui._load_local_sound('../assets/entities/water_death.wav')
    FAN_DEATH_SOUND = simplegui._load_local_sound('../assets/entities/fan_death.wav')
    GLUE_DEATH_SOUND = simplegui._load_local_sound('../assets/entities/glue_death.wav')
    FIRE_DEATH_SOUND = simplegui._load_local_sound('../assets/entities/fire_death.ogg')

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

        self.hitbox = Hitbox(self.pos, 0.6)

    # changes the current player state, which determines the players animation
    # moving state and move distance (depedant on state)
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
            Player.JUMP_SOUND.play()

        def jump_down(self):
            self.state = PlayerState.JUMP_DOWN
            self.sprite.set_animation(([0, 13], [4, 13]), 15)
            self.distance = 2
            Player.JUMP_SOUND.play()

        def jump_right(self):
            self.state = PlayerState.JUMP_RIGHT
            self.sprite.set_animation(([0, 12], [4, 12]), 15)
            self.distance = 2
            Player.JUMP_SOUND.play()

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
            PlayerState.JUMP_DOWN  : jump_down,
            PlayerState.JUMP_RIGHT : jump_right,
            PlayerState.DEAD       : dead
        }

        states[state](self)

    # check the current tile the player is standing on the determine which action to take (if any)
    # on the current frame
    def check_current_tile(self, current_tile):

        def tile_empty(self):
            pass

        def tile_solid(self):
            pass # wtf?

        def tile_icy(self):
            #self.moving = True
            self.go_idle()
            self.distance = 1
            self.move(self.pos + self.direction)

        def tile_left_fence(self):
            pass

        def tile_right_fence(self):
            pass

        def tile_up_fence(self):
            pass

        def tile_conveyor_up(self):
            #self.moving = True
            self.change_state(PlayerState.IDLE_UP)
            self.direction = Vector((0, -1))
            self.distance = 1
            self.move(self.pos + self.direction)

        def tile_conveyor_left(self):
            #self.moving = True
            self.change_state(PlayerState.IDLE_LEFT)
            self.direction = Vector((-1, 0))
            self.distance = 1
            self.move(self.pos + self.direction)

        def tile_conveyor_down(self):
            #self.moving = True
            self.change_state(PlayerState.IDLE_DOWN)
            self.direction = Vector((0, 1))
            self.distance = 1
            self.move(self.pos + self.direction)

        def tile_conveyor_right(self):
            #self.moving = True
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
            self.kill(PlayerDeath.GLUE)

        def tile_fire(self):
            self.kill(PlayerDeath.FIRE)

        def tile_fan(self):
            self.kill(PlayerDeath.FAN)

        def tile_water(self):
            self.kill(PlayerDeath.WATER)

        def tile_laser(self):
            self.kill()

        def tile_ghost(self):
            self.kill(PlayerDeath.GHOST)

        def tile_goal(self):
            clear_missiles()
            game._game.win_quote = randint(0, 6)
            game._game.change_state(game.GameState.LEVEL_COMPLETE)

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
            TileType.GLUE           : tile_glue,
            TileType.UP_FENCE       : tile_up_fence,
            TileType.FIRE           : tile_fire,
            TileType.FAN            : tile_fan,
            TileType.WATER          : tile_water,
            TileType.LASER          : tile_laser,
            TileType.GHOST          : tile_ghost,
            TileType.GOAL           : tile_goal
        }

        tiles[current_tile.type](self)

    # check the tile the player is moving into, to determine how to respond
    # in most cases this means whether the player can move into the tile or not
    # but for some unique behaviour has been defined
    def check_destination_tile(self, current_tile, destination_tile):

        def tile_empty(self, current_tile, destination_tile):
            return True

        def tile_solid(self, current_tile, destination_tile):
            return False

        def tile_icy(self, current_tile, destination_tile):
            return True

        def tile_left_fence(self, current_tile, destination_tile):
            # check if the player is moving from right to left
            if self.pos.x > self.destination.x:
                # check if the destination location isn't blocked
                jump_location = self.pos + Vector((-2, 0))
                jump_destination = tileEngine.get_tile(jump_location)
                entity = get_entity(jump_location)
                if entity:
                    if entity.ENTITY_TYPE != Panel.ENTITY_TYPE or entity.ENTITY_TYPE != LoosePanel.ENTITY_TYPE:
                        return False
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
                entity = get_entity(jump_location)
                if entity:
                    if entity.ENTITY_TYPE != Panel.ENTITY_TYPE or entity.ENTITY_TYPE != LoosePanel.ENTITY_TYPE:
                        return False
                if self.check_destination_tile(current_tile, jump_destination):
                    # change player destination and state
                    self.destination = jump_location
                    self.change_state(PlayerState.JUMP_RIGHT)
                    return True
                else:
                    return False
            else:
                return False

        def tile_up_fence(self, current_tile, destination_tile):
            # check if the player is moving down
            if self.pos.y < self.destination.y:
                # check if the destination location isn't blocked
                jump_location = self.pos + Vector((0, 2))
                jump_destination = tileEngine.get_tile(jump_location)
                entity = get_entity(jump_location)
                if entity:
                    if entity.ENTITY_TYPE != Panel.ENTITY_TYPE or entity.ENTITY_TYPE != LoosePanel.ENTITY_TYPE:
                        return False
                if self.check_destination_tile(current_tile, jump_destination):
                    # change player destination and state
                    self.destination = jump_location
                    self.change_state(PlayerState.JUMP_DOWN)
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

        def tile_fire(self, current_tile, destination_tile):
            return True

        def tile_fan(self, current_tile, destination_tile):
            return True

        def tile_water(self, current_tile, destination_tile):
            return True

        def tile_laser(self, current_tile, destination_tile):
            return True

        def tile_ghost(self, current_tile, destination_tile):
            return True

        def tile_goal(self, current_tile, destination_tile):
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
            TileType.GLUE           : tile_glue,
            TileType.UP_FENCE       : tile_up_fence,
            TileType.FIRE           : tile_fire,
            TileType.FAN            : tile_fan,
            TileType.WATER          : tile_water,
            TileType.LASER          : tile_laser,
            TileType.GHOST          : tile_ghost,
            TileType.GOAL           : tile_goal
        }

        return tiles[destination_tile.type](self, current_tile, destination_tile,)

    # checks what type of entity is in the square the player is trying to move into
    # depending on the entity type, this can have the player perform certain unique behaviour
    # such as pushing a block
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
            return True

        def missile_launcher(self, entity):
            return False

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
            Scientist.ENTITY_TYPE           : scientist,
            MissileLauncher.ENTITY_TYPE     : missile_launcher
        }

        return entities[entity.ENTITY_TYPE](self, entity)

    # checks if there is any trigger in the target location, and if so attempts to switch it
    def check_trigger(self, entity):

        if not entity.isTrigger:
            return

        def lever(self, entity):
            if self.pos.y > entity.pos.y:
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

    # sets the player to an idle state based on
    # the players last direction they were facing
    def go_idle(self):
        if not self.dead:
            self.change_state(self.state % 4)

    # places the player in a new location on the entity map
    def update_entitymap_pos(self):
        # move out of old location on entity map
        oldpos = self.pos - (self.direction * self.distance)
        if game._game.level.entitymap[oldpos.y][oldpos.x] == self.id:
            game._game.level.entitymap[oldpos.y][oldpos.x] = 0
            self.distance = None
        # move into new location on entity map
        game._game.level.entitymap[self.pos.y][self.pos.x] = self.id

    # kills the player and determines which death animation to use based on the
    # circumstances of how the player died
    def kill(self, death = PlayerDeath.SPIKE):
        if not self.dead:
            # set dead flag to true
            self.dead = True#
            self.moving = False
            # set animation looping to false
            self.sprite.loop_animations = False
            # play death animation (urgh)
            last_state = self.state % 4
            self.change_state(PlayerState.DEAD)

            # spike death
            if death == PlayerDeath.SPIKE:
                if last_state == PlayerState.IDLE_UP:
                    self.sprite.set_animation(([0, 7], [3, 7]), 10)
                elif last_state == PlayerState.IDLE_LEFT:
                    self.sprite.set_animation(([0, 8], [3, 8]), 10)
                elif last_state == PlayerState.IDLE_DOWN:
                    self.sprite.set_animation(([0, 9], [3, 9]), 10)
                elif last_state == PlayerState.IDLE_RIGHT:
                    self.sprite.set_animation(([0, 10], [3, 10]), 10)
                Player.SPIKE_DEATH_SOUND.play()
            elif death == PlayerDeath.GLUE:
                if last_state == PlayerState.IDLE_UP:
                    self.sprite.set_animation(([0, 14], [0, 14]), 10)
                elif last_state == PlayerState.IDLE_LEFT:
                    self.sprite.set_animation(([1, 14], [1, 14]), 10)
                elif last_state == PlayerState.IDLE_DOWN:
                    self.sprite.set_animation(([2, 14], [2, 14]), 10)
                elif last_state == PlayerState.IDLE_RIGHT:
                    self.sprite.set_animation(([3, 14], [3, 14]), 10)
                Player.GLUE_DEATH_SOUND.play()
            elif death == PlayerDeath.FIRE:
                if last_state == PlayerState.IDLE_UP:
                    self.sprite.set_animation(([0, 15], [3, 15]), 10)
                elif last_state == PlayerState.IDLE_LEFT:
                    self.sprite.set_animation(([0, 16], [3, 16]), 10)
                elif last_state == PlayerState.IDLE_DOWN:
                    self.sprite.set_animation(([0, 17], [3, 17]), 10)
                elif last_state == PlayerState.IDLE_RIGHT:
                    self.sprite.set_animation(([0, 18], [3, 18]), 10)
                Player.FIRE_DEATH_SOUND.play()
            elif death == PlayerDeath.FAN:
                self.sprite.set_animation(([0, 19], [6, 19]), 10)
                Player.FAN_DEATH_SOUND.play()
            elif death == PlayerDeath.WATER:
                self.sprite.set_animation(([0, 20], [4, 20]), 10)
                Player.WATER_DEATH_SOUND.play()
            elif death == PlayerDeath.GHOST:
                if last_state == PlayerState.IDLE_UP:
                    self.sprite.set_animation(([0, 21], [3, 21]), 10)
                elif last_state == PlayerState.IDLE_LEFT:
                    self.sprite.set_animation(([0, 21], [3, 21]), 10)
                elif last_state == PlayerState.IDLE_DOWN:
                    self.sprite.set_animation(([0, 21], [3, 21]), 10)
                elif last_state == PlayerState.IDLE_RIGHT:
                    self.sprite.set_animation(([0, 21], [3, 21]), 10)

            # set respawn time
            self.respawn_time = self.respawn_timer * 60

    # resets certain flas and respawns the player in
    # the player's starting location
    def respawn(self):
        clear_missiles()
        self.dead = False
        self.change_state(Player.DEFAULT_STATE)
        game._game.level.reset_level()
        self.pos = self.spawn
        self.destination = self.pos
        self.hitbox.update(self.pos)
        map_entity(self)

    def update(self): # player update method

        # check current location
        if not self.moving:
            if not self.dead:
                current_tile = tileEngine.get_tile(self.pos)
                self.check_current_tile(current_tile)

        if not self.dead:
            # check if the player is already moving or not
            if not self.moving:

                # action button
                if handlers.keyboard.m:
                    trigger_location = self.pos + self.direction
                    if self.in_bounds(trigger_location):
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
                    self.hitbox.update(self.pos)
                else:
                    self.moving = False
                    self.pos.to_int()
                    self.update_entitymap_pos()
                    self.destination = self.pos
        else:

            if self.respawn_time > 0:
                self.respawn_time -= 1
            else:
                if game._game.lives > 0:
                    game._game.lives -= 1
                    self.respawn()
                else:
                    game._game.change_state(game.GameState.GAME_OVER)

class PushBlock(Entity):

    ENTITY_TYPE = 2
    SPRITESHEET = simplegui._load_local_image('../assets/entities/pushblock.png')

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

        self.hitbox = Hitbox(self.pos, 1)

    def reset(self):
        self.pos = self.spawn
        self.dead = False
        self.dont_draw = False

        self.moving = False
        self.stuck = False
        self.sprite.set_animation(([0, 0], [0, 0]), 1)
        self.destination = self.pos
        self.hitbox.update(self.pos)
        self.direction = None

    # check the current tile the block is sitting on to determine how it should behave on the next frame
    def check_current_tile(self, current_tile):

        def tile_empty(self):
            pass

        def tile_solid(self):
            pass

        def tile_icy(self):
            #self.moving = True
            self.move(self.pos + self.direction)

        def tile_left_fence(self):
            pass

        def tile_up_fence(self):
            pass

        def tile_right_fence(self):
            pass

        def tile_conveyor_up(self):
            #self.moving = True
            self.direction = Vector((0, -1))
            self.move(self.pos + self.direction)

        def tile_conveyor_left(self):
            #self.moving = True
            self.direction = Vector((-1, 0))
            self.move(self.pos + self.direction)

        def tile_conveyor_down(self):
            #self.moving = True
            self.direction = Vector((0, 1))
            self.move(self.pos + self.direction)

        def tile_conveyor_right(self):
            #self.moving = True
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
            self.sprite.set_animation(([1, 0], [1, 0]), 1)
            pass

        def tile_fire(self):
            pass

        def tile_fan(self):
            pass

        def tile_water(self):
            pass

        def tile_laser(self):
            pass

        def tile_ghost(self):
            pass

        def tile_goal(self):
            pass

        tiles = {
            TileType.EMPTY          : tile_empty,
            TileType.SOLID          : tile_solid,
            TileType.ICY            : tile_icy,
            TileType.LEFT_FENCE     : tile_left_fence,
            TileType.UP_FENCE       : tile_up_fence,
            TileType.RIGHT_FENCE    : tile_right_fence,
            TileType.CONVEYOR_UP    : tile_conveyor_up,
            TileType.CONVEYOR_LEFT  : tile_conveyor_left,
            TileType.CONVEYOR_DOWN  : tile_conveyor_down,
            TileType.CONVEYOR_RIGHT : tile_conveyor_right,
            TileType.SPIKES         : tile_spikes,
            TileType.OPEN_PIT       : tile_open_pit,
            TileType.CLOSED_PIT     : tile_closed_pit,
            TileType.GLUE           : tile_glue,
            TileType.FIRE           : tile_fire,
            TileType.FAN            : tile_fan,
            TileType.WATER          : tile_water,
            TileType.LASER          : tile_laser,
            TileType.GHOST          : tile_ghost,
            TileType.GOAL           : tile_goal
        }

        tiles[current_tile.type](self)

    # checks the tile the block is moving into the determine whether it can move into it or not
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

        def tile_up_fence(self, current_tile, destination_tile):
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

        def tile_fire(self, current_tile, destination_tile):
            return False

        def tile_fan(self, current_tile, destination_tile):
            return False

        def tile_water(self, current_tile, destination_tile):
            return False

        def tile_laser(self, current_tile, destination_tile):
            return False

        def tile_ghost(self, current_tile, destination_tile):
            return False

        def tile_goal(self, current_tile, destination_tile):
            return False


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
            TileType.GLUE           : tile_glue,
            TileType.UP_FENCE       : tile_up_fence,
            TileType.FIRE           : tile_fire,
            TileType.FAN            : tile_fan,
            TileType.WATER          : tile_water,
            TileType.LASER          : tile_laser,
            TileType.GHOST          : tile_ghost,
            TileType.GOAL           : tile_goal
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

        def missile_launcher(self, entity):
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
            Scientist.ENTITY_TYPE            : scientist,
            MissileLauncher.ENTITY_TYPE      : missile_launcher
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
                self.hitbox.update(self.pos)
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
    SPRITESHEET = simplegui._load_local_image('../assets/entities/triggers/lever.png')
    SWITCH_SOUND = simplegui._load_local_sound('../assets/entities/triggers/switch_lever.wav')

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
            Lever.SWITCH_SOUND.play()

            if self.on:
                self.sprite.set_animation(([1, 0], [1, 0]), 1)
            else:
                self.sprite.set_animation(([0, 0], [0, 0]), 1)

    def contact_data(self):
        if len(self.contacts) != 0:
            string = ""
            for i in range(len(self.contacts)):
                if (i + 1) < len(self.contacts):
                    string += str(self.id) + "," + str(self.contacts[i].id) + "\n"
                else:
                    string += str(self.id) + "," + str(self.contacts[i].id)
            return string

class Button(Trigger):

    ENTITY_TYPE = 4
    SPRITESHEET = simplegui._load_local_image('../assets/entities/triggers/button.png')
    SWITCH_SOUND = simplegui._load_local_sound('../assets/entities/triggers/carbuncle.wav')

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
                Button.SWITCH_SOUND.play()

                if self.on:
                    self.time = self.timer
                    self.sprite.set_animation(([1, 0], [1, 0]), 1)
                else:
                    self.time = 0
                    self.sprite.set_animation(([0, 0], [0, 0]), 1)

    def contact_data(self):
        string = str(self.id) + "," + str(self.contact.id)
        return string

    def update(self):

        # check timer
        if self.on:
            if self.time > 0:
                self.time -= 1
            if self.time == 0:
                self.switch()

    def save_data(self):
        string = str(self.ENTITY_TYPE) + "," + str(self.spawn).strip("()") + "," + str(self.timer // 60)
        return string

class Panel(Trigger):

    ENTITY_TYPE = 5
    SPRITESHEET = simplegui._load_local_image('../assets/entities/triggers/panel.png')

    PANEL_UP_SOUND = simplegui._load_local_sound('../assets/entities/triggers/panel_up.wav')
    PANEL_DOWN_SOUND = simplegui._load_local_sound('../assets/entities/triggers/panel_down.wav')

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
                unmap_entity(self)
                self.sprite.set_animation(([1, 0], [1, 0]), 1)
                Panel.PANEL_DOWN_SOUND.play()
            else:
                map_entity(self)
                self.sprite.set_animation(([0, 0], [0, 0]), 1)
                Panel.PANEL_UP_SOUND.play()

    def contact_data(self):
        if len(self.contacts) != 0:
            string = ""
            for i in range(len(self.contacts)):
                if (i + 1) < len(self.contacts):
                    string += str(self.id) + "," + str(self.contacts[i].id) + "\n"
                else:
                    string += str(self.id) + "," + str(self.contacts[i].id)
            return string

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
    SPRITESHEET = simplegui._load_local_image('../assets/entities/triggers/loose_panel.png')

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
                unmap_entity(self)
                self.sprite.set_animation(([1, 0], [1, 0]), 1)
                Panel.PANEL_DOWN_SOUND.play()
            else:
                map_entity(self)
                self.sprite.set_animation(([0, 0], [0, 0]), 1)
                Panel.PANEL_UP_SOUND.play()

    def contact_data(self):
        if len(self.contacts) != 0:
            string = ""
            for i in range(len(self.contacts)):
                if (i + 1) < len(self.contacts):
                    string += str(self.id) + "," + str(self.contacts[i].id) + "\n"
                else:
                    string += str(self.id) + "," + str(self.contacts[i].id)
            return string

    def update(self):

        if self.on:
            # check if there is anything keeping it pressed down
            if not get_entity(self.pos):
                self.switch()

class Door(Entity):

    OPEN_SOUND = simplegui._load_local_sound("../assets/entities/doors/hatch_open.wav")

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

        # check potential obstructions
        for entity in Entity.entity_moveable:
            if self.pos == entity.destination:
                return False

        self.open = not self.open

        if self.open:
            # Door.OPEN_SOUND.play()
            unmap_entity(self)
            self.sprite.set_animation(([1, 0], [1, 0]), 1)
        else:
            map_entity(self)
            self.sprite.set_animation(([0, 0], [0, 0]), 1)

        return True

class VerticalDoor(Door):

    ENTITY_TYPE = 7
    SPRITESHEET = simplegui._load_local_image('../assets/entities/doors/vert_door.png')

    def __init__(self, pos):

        Door.__init__(self, pos)
        self.img = VerticalDoor.SPRITESHEET
        self.sprite = Sprite(self.img)

        self.open = False

class HorizontalDoor(Door):

    ENTITY_TYPE = 8
    SPRITESHEET = simplegui._load_local_image('../assets/entities/doors/hori_door.png')

    def __init__(self, pos):

        Door.__init__(self, pos)
        self.img = HorizontalDoor.SPRITESHEET
        self.sprite = Sprite(self.img)

        self.open = False

class VerticalTimedDoor(Door):

    ENTITY_TYPE = 9
    SPRITESHEET = simplegui._load_local_image("../assets/entities/doors/vert_timed_door.png")

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

                # check for potential obstructions
                for entity in Entity.entity_moveable:
                    if self.pos == entity.destination:
                        return False

                # if no obstuctions are found, close the door
                self.open = False
                map_entity(self)
                self.sprite.set_animation(([0, 0], [0, 0]), 1)

    def save_data(self):
        string = str(self.ENTITY_TYPE) + "," + str(self.spawn).strip("()") + "," + str(self.timer // 60)
        return string

class HorizontalTimedDoor(Door):

    ENTITY_TYPE = 10
    SPRITESHEET = simplegui._load_local_image("../assets/entities/doors/hori_timed_door.png")

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

                # check for potential obstructions
                for entity in Entity.entity_moveable:
                    if self.pos == entity.destination:
                        return False

                # if no obstuctions are found, close the door
                self.open = False
                map_entity(self)
                self.sprite.set_animation(([0, 0], [0, 0]), 1)

    def save_data(self):
        string = str(self.ENTITY_TYPE) + "," + str(self.spawn).strip("()") + "," + str(self.timer // 60)
        return string


class ScientistState(IntEnum):

    WALK_UP    = 1
    WALK_LEFT  = 2
    WALK_DOWN  = 3
    WALK_RIGHT = 4

class Scientist(Entity):

    ENTITY_TYPE = 11
    SPRITESHEET = simplegui._load_local_image("../assets/entities/scientist.png")
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

    # set and initilizes the patrol route of a scientist
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

    # changes the direction of the scientist so they walk in the
    # opposite direction to the one they were before
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

    # determines how the scientist behaves in each different state
    # essentially just determines walk direction and animations
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

    # determines how the scientist behaves when it comes into contact with different entities
    def check_entity(self, entity): # scientist check entity method

        def player(self, entity):
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

        def missile_launcher(self, entity):
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
            Scientist.ENTITY_TYPE           : scientist,
            MissileLauncher.ENTITY_TYPE     : missile_launcher
        }

        return entities[entity.ENTITY_TYPE](self, entity)

    # resets the scientist to its spawn location
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

    # checks if the player is in attack range and kills the player if so
    def check_player(self):
        player = Entity.entities[0]
        dist = player.pos - self.pos
        if dist.dot(dist) < 0.25:
            player.kill()

    def update(self):

        # check if player is in killing range
        self.check_player()

        if self.moving:

            # moves the scientist forward to its target destination
            if self.pos != self.destination:
                self.pos += (self.direction * self.speed)
            else:
                self.pos.to_int()
                self.update_entitymap_pos()

                # switches direction when the patrol point has been reached
                if self.pos == self.patrol:
                    self.change_direction()
                elif self.pos == self.spawn:
                    self.change_direction()
                else:
                    self.move(self.pos + self.direction)

    def save_data(self):
        string = str(self.ENTITY_TYPE) + "," + str(self.spawn).strip("()") + "," + str(self.patrol).strip("()")
        return string

class MissileLauncher(Entity):

    ENTITY_TYPE = 12
    SPRITESHEET = simplegui._load_local_image("../assets/entities/missile_launcher.png")
    LAUNCH_SOUND = simplegui._load_local_sound("../assets/entities/launch.wav")

    # todo: player in range sound

    # pre calculate angles
    TOP_LEFT     = math.pi * 0.25
    TOP_RIGHT    = 3 * math.pi * 0.25
    BOTTOM_LEFT  = -TOP_LEFT
    BOTTOM_RIGHT = -TOP_RIGHT

    def __init__(self, pos):

        Entity.__init__(self, pos)
        self.img = MissileLauncher.SPRITESHEET
        self.sprite = Sprite(self.img)

        self.range = 5 # the range for how close the player must be before the launcher will open fire
        self.fuse  = 10 # the timer for how long the launcher's missiles will last
        self.range_sq = self.range * self.range # pre calculated squared range to speed up range checks
        self.fired = False #  a flag indicating whether or not the launcher has a missile currently active
        self.angle = 0 # the direction the launcher is facing

    # set the range for how close the player must be before the launcher will open fire
    def set_range(self, range):
        self.range = range
        self.range_sq = self.range * self.range

    # set the timer for how long the launcher's missiles will last
    def set_fuse(self, fuse):
        self.fuse = fuse

    # checks if the player is in firing in range
    def check_range(self, player):
        dist_vec = player.pos - self.pos
        distance = dist_vec.dot(dist_vec)
        if distance < self.range_sq:
            return True
        return False

    # rotate the missile launcher to face towards the player
    def face_player(self, player, direction):
        angle = direction.angle()
        self.angle = angle

    # checks if the player is in range and fires if a missile if there
    # isn't already one currently active from the missile launcher
    def update(self):
        player = Entity.entities[0]
        if not player.dead:
            if self.check_range(player):
                direction = player.pos - self.pos
                self.face_player(player, direction)
                if not self.fired:
                    Missile(self.pos, direction, self)
                    MissileLauncher.LAUNCH_SOUND.play()
                    self.fired = True

    def draw(self, canvas):

        # only draws when on screen
        left = int(game._game.camera.pos.x)
        if self.pos.x < left : return
        if self.pos.x > min(left + int(tileEngine.MAX_TILES_X) + 1, len(game._game.level.tilemap.map[0])): return

        top = int(game._game.camera.pos.y)
        if self.pos.y < top: return
        if self.pos.y > min(top + int(tileEngine.MAX_TILES_Y) + 1, len(game._game.level.tilemap.map)): return

        self.sprite.rot_draw(canvas, self.pos, self.angle)

    # generates a save data string for the missile launcher
    def save_data(self):
        string = str(self.ENTITY_TYPE) + "," + str(self.spawn).strip("()") + "," + str(self.range) + "," + str(self.fuse)
        return string

# base class for projectiles. Stores all currently active projectiles
# and provides a direction and position vector, as well as a hitbox for
# all projectiles ragardless of their type
class Projectile:

    projectiles = [] #list of all currently active projectiles

    def __init__(self, pos, direction):

        self.pos = pos # projectiles current position
        self.direction = direction.normalize() # projectiles direction / velocity vector
        self.hitbox = Hitbox(pos, 0.6) # projectiles hitbox

        Projectile.projectiles.append(self)

# explodes all currently active missiles
def clear_missiles():
    for missile in Projectile.projectiles:
        missile.explode()

class Missile(Projectile):

    SPRITESHEET = simplegui._load_local_image("../assets/entities/missile.png")
    SPEED = 1 / 64 # missiles movement speed
    EXPLODE_SOUND = simplegui._load_local_sound("../assets/entities/boom1.wav")

    # pre calculate angles to save processing on collisions later
    CENTER       = Vector((17, 15))
    TOP_LEFT     = (Vector((0 , 12)) - CENTER).angle()
    TOP_RIGHT    = (Vector((31, 12)) - CENTER).angle()
    BOTTOM_RIGHT = (Vector((31, 19)) - CENTER).angle()
    BOTTOM_LEFT  = (Vector((0 , 19)) - CENTER).angle()
    LENGTH       = 15

    def __init__(self, pos, direction, launcher):

        Projectile.__init__(self, pos, direction)

        # source image for the missile
        self.img = Missile.SPRITESHEET
        self.sprite = Sprite(self.img)

        self.launcher = launcher # the missile launcher which fired the missile
        self.angle = 0 # the current direction the missile is facing and moving
        self.timer = launcher.fuse # the maximum amount of time the missile can be active for
        self.time = self.timer * 60 # the amount fo time left before the missile explodes

        self.exploded = False # tracks whether the missile has exploded or not

    # determines which way the missile should flay based on the players location relative to the missile's
    def get_direction(self):
        player = Entity.entities[0]
        self.direction = (player.pos - self.pos).normalize()
        self.angle = self.direction.angle()

    # has the missile explode. plays the exploding sound and animation and sets the eploded flag to true
    def explode(self):
        self.sprite.set_animation(([1, 0], [8, 0]), 5)
        self.sprite.loop_animations = False
        Missile.EXPLODE_SOUND.play()
        self.exploded = True

    def check_collisions(self):

        # get the true center position of the missile
        pos = Vector((HALFSIZE + (self.pos.x * TILESIZE), HALFSIZE + (self.pos.y * TILESIZE)))

        # calculate contact points (these are used to find if the missile has hit anything solid)
        contact_points = [
            (pos + Vector((math.cos(Missile.TOP_LEFT     + self.angle), math.sin(Missile.TOP_LEFT     + self.angle))) * Missile.LENGTH).to_grid(),
            (pos + Vector((math.cos(Missile.TOP_RIGHT    + self.angle), math.sin(Missile.TOP_RIGHT    + self.angle))) * Missile.LENGTH).to_grid(),
            (pos + Vector((math.cos(Missile.BOTTOM_LEFT  + self.angle), math.sin(Missile.BOTTOM_LEFT  + self.angle))) * Missile.LENGTH).to_grid(),
            (pos + Vector((math.cos(Missile.BOTTOM_RIGHT + self.angle), math.sin(Missile.BOTTOM_RIGHT + self.angle))) * Missile.LENGTH).to_grid()
        ]

        # the missile explodes if it comes into contact with any solid tiles
        for p in contact_points:
            tile = tileEngine.get_tile(p)
            if tile.type == TileType.SOLID:
                self.explode()
                return

            # the missile explodes if it comes into contact with any doors
            entity = get_entity(p)
            if entity:
                if entity.isDoor:
                    if not entity.open:
                        self.explode()
                        return

        # new collision detection for missile vs box (invincibility glitch fix)
        for entity in Entity.entities:
            if entity.ENTITY_TYPE == PushBlock.ENTITY_TYPE:
                for p in contact_points:
                    if entity.hitbox.intersect(p * TILESIZE):
                        self.explode()
                        return

        # obligatory bounding volume overlap test to meet the spec
        player = Entity.entities[0]
        if self.hitbox.overlap(player.hitbox):
            self.explode()
            player.kill()

    def update(self):

        # actions to be performed if the missile has yet to explode
        if not self.exploded:
            # check missile timer
            if self.time > 0:
                self.time -= 1
            else:
                self.explode()

        # actions to be performed if the missile has yet to explode
        if not self.exploded:
            # check for collisions with walls
            self.get_direction()
            self.check_collisions()

        # actions to be performed if the missile has already exploded
        if self.exploded:
            # check if the explosion animation has finished
            if self.sprite.current_index == [8, 0]:
                # delete the missile
                Projectile.projectiles.remove(self)
                # prepare launcher to fire again
                self.launcher.fired = False
            return

        # move missile
        self.pos += (self.direction * Missile.SPEED)
        self.hitbox.update(self.pos)

    # draws and rotate the missile
    def draw(self, canvas):
        self.sprite.rot_draw(canvas, self.pos, self.angle)

# hitboxes are used to detect collisions between certain entities
class Hitbox:

    #SIZE = TILESIZE * 0.6

    def __init__(self, pos, scale):

        self.pos = (pos * TILESIZE) - Vector((HALFSIZE, HALFSIZE))
        self.size = TILESIZE * scale

    # checks if two hitboxes are overlapping
    def overlap(self, hitbox):
        if self.pos.x + self.size < hitbox.pos.x: return False
        elif self.pos.x > hitbox.pos.x + self.size: return False
        elif self.pos.y + self.size < hitbox.pos.y: return False
        elif self.pos.y > hitbox.pos.y + self.size: return False
        return True

    # checks if a point is inside the hitbox
    def intersect(self, p):

        if p.x < self.pos.x: return False
        if p.x > self.pos.x + self.size: return False
        if p.y < self.pos.y: return False
        if p.y > self.pos.y + self.size: return False
        return True

    # repositions the hitbox given a position vector
    def update(self, pos):
        self.pos = (pos * TILESIZE) - Vector((HALFSIZE, HALFSIZE))

# retrieves an entities id via it's position in the entity map
def get_entity(pos):
    entity_id = game._game.level.entitymap[pos.y][pos.x]
    if bool(entity_id):
        return Entity.entities[entity_id - 1]
    else:
        return False

# place an entity within the entity map
def map_entity(entity):
    game._game.level.entitymap[entity.pos.y][entity.pos.x] = entity.id

# remove an entity from the entity map
def unmap_entity(entity):
    game._game.level.entitymap[int(entity.pos.y)][int(entity.pos.x)] = 0
