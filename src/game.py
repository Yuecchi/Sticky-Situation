try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from enum import IntEnum

import handlers
from vectors import Vector
from tileEngine import Tilesheet
from tileEngine import Tilemap
from entities   import Entity
from entities   import Player
from entities   import PlayerState
from entities   import PushBlock
from level      import Level
from camera     import Camera

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
        self.camera = Camera()

    def change_state(self, state):
        self.state = state

    def change_level(self, level):
        self.level = level

    def draw(self, canvas):

        # update shit here (player pos, ai scripts, blah blah blah
        for entity in Entity.entities:
            entity.update()

        if self.camera.anchor:
            self.camera.update()

        self.level.tilemap.draw(canvas)
        for entity in Entity.entities:
            entity.draw(canvas)

        canvas.draw_text(str(player.pos), (0, 16), 16, "White")
        canvas.draw_text(str(self.camera.pos), (0, 32), 16, "White")

        """
        for i in range(len(entitymap)):
            canvas.draw_text(str(self.level.entitymap[i]), (400, 16 + (i * 16)), 16, "White")

        canvas.draw_text(str(player.state), (0, 320), 16, "White")
        canvas.draw_text(str(player.moving), (0, 336), 16, "White")
        canvas.draw_text(str(player.pos), (0, 352), 16, "White")

        canvas.draw_text(str(block.moving), (0, 384), 16, "White")
        canvas.draw_text(str(block.destination), (0, 400), 16, "White")
        """

        self.clock.tick()

_game = Game()

# TODO: EVERTYTHING BELOW HERE IS TEST DATA WHICH WILL BE LOADED VIA LEVEL FILES LATER

# testing tilesheets
testsheet = simplegui._load_local_image('../assets/testsheet.png')
testsprite = simplegui._load_local_image('../assets/testsprite.png')
testblock = simplegui._load_local_image('../assets/testblock.png')
horse = simplegui._load_local_image('../assets/SS_Horse_1.1.png')

index = (1, 1, 10, 1)
types = (0, 0, 0 , 1)

tilesheet = Tilesheet(testsheet, index, types)
tilesheet.tiles[2].set_animation_speed(8)

""""
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
"""

t_map = [
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 2, 2, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
]

tilemap = Tilemap(tilesheet, t_map)

# testing entities
entitymap = [
    [
        0 for x in range(len(t_map[0]))
    ] for y in range(len(t_map))
]

player = Player(Vector((1, 1)), horse)
_game.camera.set_anchor(player)
player.change_state(PlayerState.IDLE_RIGHT)


block  = PushBlock(Vector((3, 6)), testblock)

level = Level(tilemap, entitymap)
_game.change_level(level)
_game.camera.set_max_scroll(_game.level.tilemap)

# TODO:
#  setting camera's max scroll in anchor will have to be part of
#  level loading, there will need to be some way of always identifying
#  the character entity in order to correctly anchor the camera



