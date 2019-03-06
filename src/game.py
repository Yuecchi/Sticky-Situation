try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from enum import IntEnum
from vectors import Vector

import handlers

from tileEngine import Tilesheet
from tileEngine import Tilemap
from entities   import Entity
from entities   import Player
from entities   import PlayerState
from entities   import PushBlock
from level      import Level

class Clock:

    def __init__(self):
        self.t = 0

    def tick(self):
        self.t += 1

    def transition(self, rate):
        return not(self.t % rate)

class GameState(IntEnum):

    TITLE = 1

class Game:

    def __init__(self):

        self.state = GameState.TITLE
        self.level = None
        self.clock = Clock()

    def change_state(self, state):
        self.state = state

    def change_level(self, level):
        self.level = level

    def draw(self, canvas):

        # update shit here (player pos, ai scripts, blah blah blah
        player.update(handlers.keyboard)

        self.level.tilemap.draw(canvas)
        for entity in Entity.entities:
            entity.draw(canvas)

        for i in range(len(entitymap)):
            canvas.draw_text(str(self.level.entitymap[i]), (400, 16 + (i * 16)), 16, "White")

        canvas.draw_text(str(player.state), (0, 320), 16, "White")

        self.clock.tick()

_game = Game()

# TODO: EVERTYTHING BELOW HERE IS TEST DATA WHICH WILL BE LOADED VIA LEVEL FILES LATER

# testing tilesheets
testsheet = simplegui._load_local_image('../assets/testsheet.png')
testsprite = simplegui._load_local_image('../assets/testsprite.png')
testblock = simplegui._load_local_image('../assets/testblock.png')
horse = simplegui._load_local_image('../assets/SS_Horse_1.1.png')

index = (1, 1, 10, 1)
types = (0, 0, 1 , 1)

tilesheet = Tilesheet(testsheet, index, types)
tilesheet.tiles[2].set_animation_speed(8)

t_map = [
    [2, 3, 3, 3, 3, 3, 3, 3, 3, 2],
    [3, 0, 0, 0, 3, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 3, 0, 3, 0, 0, 3],
    [3, 3, 3, 3, 3, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [2, 3, 3, 3, 3, 3, 3, 3, 3, 2],
]

tilemap = Tilemap(tilesheet, t_map)

# testing entities
entitymap = [
    [
        0 for x in range(len(t_map[0]))
    ] for y in range(len(t_map))
]

player = Player(Vector((1, 1)), horse)
player.change_state(PlayerState.IDLE_RIGHT)

block  = PushBlock(Vector((3, 6)), testblock)

level = Level(tilemap, entitymap)
_game.change_level(level)




