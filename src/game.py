try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from enum import IntEnum
from vectors import Vector
from tileEngine import Tilesheet
from tileEngine import Tilemap
import entities
from entities   import Entity
from entities   import Player
from entities   import PlayerState
from entities   import PushBlock
from entities   import Lever
from entities   import Button
from entities   import Panel
from entities   import LoosePanel
from entities   import Door
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
        for entity in Entity.entities[::-1]:
            entity.draw(canvas)

        canvas.draw_text("player position: " + str(player.pos), (0, 16), 16, "White")
        canvas.draw_text("player direction: " + str(player.direction), (0, 32), 16, "White")
        canvas.draw_text("player state: " + str(player.state), (0, 48), 16, "White")

        """
        canvas.draw_text(str(button.on), (0, 64), 16, "White")
        canvas.draw_text(str(round(button.time / 60, 1)), (0, 80), 16, "White")

        
        canvas.draw_text(str(player.pos), (0, 16), 16, "White")
        canvas.draw_text(str(self.camera.pos), (0, 32), 16, "White")


        for i in range(len(entitymap)):
            canvas.draw_text(str(self.level.entitymap[i]), (0, 16 + (i * 16)), 16, "White")

        canvas.draw_text(str(player.state), (0, 320), 16, "White")
        canvas.draw_text(str(player.moving), (0, 336), 16, "White")
        canvas.draw_text(str(player.pos), (0, 352), 16, "White")

        canvas.draw_text(str(block.moving), (0, 384), 16, "White")
        canvas.draw_text(str(block.destination), (0, 400), 16, "White")
        """

        for i in range(len(entitymap)):
            canvas.draw_text(str(self.level.entitymap[i]), (0, 16 + (i * 16)), 16, "White")

        self.clock.tick()

_game = Game()

# TODO: EVERTYTHING BELOW HERE IS TEST DATA WHICH WILL BE LOADED VIA LEVEL FILES LATER

# testing tilesheets
testsheet = simplegui._load_local_image('../assets/testsheet.png')

testsprite = simplegui._load_local_image('../assets/testsprite.png')
testblock = simplegui._load_local_image('../assets/testblock.png')
horse = simplegui._load_local_image('../assets/SS_Horse_1.1.png')
testlever = simplegui._load_local_image('../assets/lever.png')
testdoor = simplegui._load_local_image('../assets/door.png')
testbutton = simplegui._load_local_image('../assets/button.png')

test_panel = simplegui._load_local_image('../assets/panel.png')
test_loose_panel = simplegui._load_local_image('../assets/loose_panel.png')

index  = (1, 1, 10, 1, 1, 1, 1, 1, 1, 1, 1, 3 , 3 , 3 , 3 , 5 )
types  = (0, 2, 0 , 1, 1, 1, 1, 3, 4, 1, 1, 5 , 6 , 7 , 8 , 9 )
speeds = (1, 1, 8 , 1, 1, 1, 1, 1, 1, 1, 1, 15, 15, 15, 15, 15)

tilesheet = Tilesheet(testsheet, index, types, speeds)

t_map = [
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 0, 3, 3, 3, 3, 3, 0, 3, 3, 3, 3, 3, 0, 3, 3, 3, 3, 3, 3, 3, 3, 0, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 4, 5, 5, 5, 6, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 1, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 9, 5, 0, 5, 10, 0, 0, 0, 0, 0, 1, 0, 0, 2, 2, 2, 0, 0, 1, 0, 3, 3, 3, 0, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 13, 12, 12, 12, 12, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 13, 0, 0, 0, 0, 11, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 13, 0, 0, 0, 0, 11, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 13, 0, 0, 0, 0, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 13, 0, 0, 0, 0, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 14, 14, 14, 14, 14, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
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

level = Level(tilemap, entitymap)
level.set_spawn(Vector((3, 3)))

_game.change_level(level)
_game.camera.set_max_scroll(_game.level.tilemap)

player = Player(Vector((18, 28)), horse)
_game.camera.set_anchor(player)
player.change_state(PlayerState.IDLE_DOWN)

block1  = PushBlock(Vector((9, 3)), testblock)
block2 = PushBlock(Vector((23, 2)), testblock)
block3 = PushBlock(Vector((27, 12)), testblock)

lever = Lever(Vector((5, 0)), testlever)
lever_door = Door(Vector((3, 6)), testdoor)
lever.set_contact(lever_door)

button = Button(Vector((17, 0)), testbutton)
button.set_timer(7)
button_door = Door(Vector((15, 6)), testdoor)
button.set_contact(button_door)

panel = Panel(Vector((27, 13)), test_panel)
panel_door = Door(Vector((26, 16)), testdoor)
panel.set_contact(panel_door)
panel_lever = Lever(Vector((26, 10)), testlever)
panel_lever.set_contact(panel)

loose_panel = LoosePanel(Vector((25, 3)), test_loose_panel)
loose_panel_door = Door(Vector((24, 6)), testdoor)
loose_panel.set_contact(loose_panel_door)

_game.level.store_reset_maps()

# TODO:
#  setting camera's max scroll in anchor will have to be part of
#  level loading, there will need to be some way of always identifying
#  the character entity in order to correctly anchor the camera