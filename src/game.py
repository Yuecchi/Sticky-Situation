try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from enum import IntEnum
from vectors import Vector
import tileEngine
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
import level
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
        self.camera.set_max_scroll(self.level.tilemap)

    def draw(self, canvas):

        # update shit here (player pos, ai scripts, blah blah blah
        for entity in Entity.entity_updates:
            entity.update()

        if self.camera.anchor:
            self.camera.update()

        self.level.tilemap.draw(canvas)

        for entity in Entity.entity_drawing[::-1]:
            entity.draw(canvas)

        """
        canvas.draw_text("player position: " + str(player.pos), (0, 16), 16, "White")
        canvas.draw_text("player direction: " + str(player.direction), (0, 32), 16, "White")
        canvas.draw_text("player state: " + str(player.state), (0, 48), 16, "White")
        
        
        for i in range(len(self.level.entitymap)):
            canvas.draw_text(str(self.level.entitymap[i]), (0, 16 + (i * 16)), 16, "White")
        """

        #canvas.draw_text(str(block4.direction), (0, 16), 16, "White")
        #canvas.draw_text(str(block4.destination), (0, 32), 16, "White")
        #canvas.draw_text(str(block4.moving), (0, 48), 16, "White")

        self.clock.tick()

_game = Game()

# TODO: EVERTYTHING BELOW HERE IS TEST DATA WHICH WILL BE LOADED VIA LEVEL FILES LATER


testsprite = simplegui._load_local_image('../assets/testsprite.png')
testblock = simplegui._load_local_image('../assets/testblock.png')
horse = simplegui._load_local_image('../assets/SS_Horse_1.1.png')
testlever = simplegui._load_local_image('../assets/lever.png')
testdoor = simplegui._load_local_image('../assets/door.png')
testbutton = simplegui._load_local_image('../assets/button.png')
test_panel = simplegui._load_local_image('../assets/panel.png')
test_loose_panel = simplegui._load_local_image('../assets/loose_panel.png')


"""
testsheet_path = '../assets/testsheet.png'
index  = [1, 1, 10, 1, 1, 1, 1, 1, 1, 1, 1, 3 , 3 , 3 , 3 , 5 , 1 , 1 ]
types  = [0, 2, 0 , 1, 1, 1, 1, 3, 4, 1, 1, 5 , 6 , 7 , 8 , 9 , 10, 11]
speeds = [1, 1, 8 , 1, 1, 1, 1, 1, 1, 1, 1, 15, 15, 15, 15, 15, 1 , 1 ]
tilesheet = Tilesheet(testsheet_path, index, types, speeds)
tilesheet.save("../assets/testsheet.txt")

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
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 15, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
]
tilemap = Tilemap(tilesheet, t_map)
tilemap.save('../assets/testmap.txt')
"""

# tilesheet = tileEngine.load_tilesheet('../assets/testsheet.txt')
# testmap = tileEngine.load_tilemap('../assets/mapsmall.txt')

testmap = tileEngine.load_tilemap('../assets/testmap.txt')
level = Level(testmap)
_game.change_level(level)
player = Player(Vector((8, 17)), horse)
_game.camera.set_anchor(player)

block1 = PushBlock(Vector((9, 3)), testblock)
block2 = PushBlock(Vector((23, 2)), testblock)
block3 = PushBlock(Vector((27, 12)), testblock)
block4 = PushBlock(Vector((18, 26)), testblock)
block4 = PushBlock(Vector((5, 24)), testblock)
block5 = PushBlock(Vector((8, 18)), testblock)

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

temp = []
for entity in Entity.entities:
    if entity.ENTITY_TYPE == PushBlock.ENTITY_TYPE:
        temp.append(entity)
    else:
        Entity.entity_updates.append(entity)
Entity.entity_updates.extend(temp)

temp = []
for entity in Entity.entities:
    if entity.isTrigger:
        temp.append(entity)
    else:
        Entity.entity_drawing.append(entity)
Entity.entity_drawing.extend(temp)

_game.level.store_reset_maps()

# level.save("../assets/level.txt")
# level.load_level("../assets/level.txt")