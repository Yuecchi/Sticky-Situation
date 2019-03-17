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
from entities   import VerticalDoor
from entities   import HorizontalDoor
from entities   import VerticalTimedDoor
from entities   import HorizontalTimedDoor
from entities   import Scientist
from entities   import ScientistState
from entities   import MissileLauncher
from entities   import Projectile
from entities   import Missile
import level
from level      import Level
from camera     import Camera
import menu
import handlers

FRAMEWIDTH, FRAMEHEIGHT = 640, 480

class Clock:

    def __init__(self):
        self.t = 0

    def tick(self):
        self.t += 1

    def transition(self, rate):
        return not(self.t % rate)

    def reset(self):
        self.t = 0

class GameState(IntEnum):

    TITLE = 1
    GAME  = 2

class Game:

    TITLE_BG = simplegui._load_local_image("../assets/title_menu//title_background.png")

    def __init__(self):

        self.state = GameState.TITLE
        self.level = None
        self.clock = Clock()
        self.camera = Camera()

        self.mouse = handlers.mouse
        self.title_menu = menu.title_menu

    def start(self):
        level.load_level("../assets/levels/elliot.txt")
        self.change_state(GameState.GAME)

    def initialize_title_menu(self):
        self.title_menu.options[0].set_action(self.start)
        self.title_menu.options[1].set_action(exit)

    def change_state(self, state):
        self.state = state

    def change_level(self, level):
        self.level = level
        self.camera.set_max_scroll(self.level.tilemap)

    def draw(self, canvas):

        if self.state == GameState.TITLE:

            # display tile screen background image
            src_pos  = (Game.TITLE_BG.get_width() / 2, Game.TITLE_BG.get_height() / 2)
            src_dims = (Game.TITLE_BG.get_width(), Game.TITLE_BG.get_height())
            canvas.draw_image(Game.TITLE_BG, src_pos, src_dims, src_pos, src_dims)

            # check for menu option interaction
            self.title_menu.update(self.mouse)

            # display title menu options
            self.title_menu.display(canvas)

        if self.state == GameState.GAME:

            # update shit here (player pos, ai scripts, blah blah blah
            for entity in Entity.entity_updates:
                entity.update()

            for projectile in Projectile.projectiles:
                projectile.update()

            if self.camera.anchor:
                self.camera.update()

            self.level.tilemap.draw(canvas)

            for entity in Entity.entity_drawing[::-1]:
                entity.draw(canvas)

            for projectile in Projectile.projectiles:
                projectile.draw(canvas)

        """
        canvas.draw_text("player position: " + str(player.pos), (0, 16), 16, "White")
        canvas.draw_text("player direction: " + str(player.direction), (0, 32), 16, "White")
        canvas.draw_text("player state: " + str(player.state), (0, 48), 16, "White")
        
        
        for i in range(len(self.level.entitymap)):
            canvas.draw_text(str(self.level.entitymap[i]), (0, 16 + (i * 16)), 16, "White")
        """

        self.mouse.reset()
        self.clock.tick()

_game = Game()
_game.initialize_title_menu()


# TODO: EVERTYTHING BELOW HERE IS TEST DATA WHICH WILL BE LOADED VIA LEVEL FILES LATER
"""
testsheet_path = '../assets/testsheet.png'
index  = [1, 1, 10, 1, 1, 1, 1, 1, 1, 1, 1, 3 , 3 , 3 , 3 , 5 , 1 , 1 , 4 ]
types  = [0, 2, 0 , 1, 1, 13, 1, 3, 4, 1, 1, 5 , 6 , 7 , 8 , 9 , 10, 11, 12]
speeds = [1, 1, 8 , 1, 1, 1, 1, 1, 1, 1, 1, 15, 15, 15, 15, 15, 1 , 1 , 10]
tilesheet = Tilesheet(testsheet_path, index, types, speeds)
# tilesheet.save("../assets/testsheet.txt")

t_map = [
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 3, 3, 0, 3, 3, 3, 3, 3, 0, 3, 3, 3, 3, 3, 3, 0, 3, 0, 3, 0, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 4, 5, 5, 5, 6, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 7, 0, 0, 0, 8, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 1, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 9, 5, 0, 5, 10, 0, 0, 0, 0, 0, 1, 0, 0, 2, 2, 2, 0, 0, 1, 0, 3, 0, 3, 0, 3, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 13, 12, 12, 12, 12, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 13, 0, 0, 0, 0, 11, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 13, 0, 0, 0, 0, 11, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 13, 0, 0, 0, 0, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 0, 3, 3, 3],
    [3, 0, 0, 13, 0, 0, 0, 0, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 14, 14, 14, 14, 14, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 3, 0, 3, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 15, 0, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
]
testmap = Tilemap(tilesheet, t_map)

# tilemap.save('../assets/testmap.txt')
# tilesheet = tileEngine.load_tilesheet('../assets/testsheet.txt')
# testmap = tileEngine.load_tilemap('../assets/mapsmall.txt')
# testmap = tileEngine.load_tilemap('../assets/testmap.txt')

level = Level(testmap)

_game.change_level(level)
player = Player(Vector((25, 5)))
_game.camera.set_anchor(player)

block1 = PushBlock(Vector((9, 3)))
block2 = PushBlock(Vector((23, 2)))
block3 = PushBlock(Vector((27, 12)))
block4 = PushBlock(Vector((18, 26)))
block5 = PushBlock(Vector((9, 16)))
block6 = PushBlock(Vector((8, 23)))
block7 = PushBlock(Vector((21, 2)))

lever1 = Lever(Vector((5, 0)))
lever_door = []
for i in range(5):
    lever_door.append(VerticalDoor(Vector((1 + i, 6))))
    lever1.add_contact(lever_door[i])

hori_lever_door = HorizontalDoor(Vector((6, 3)))
lever1.add_contact(hori_lever_door)

button = Button(Vector((17, 0)))
button.set_timer(7)
button_door = VerticalDoor(Vector((15, 6)))
button.set_contact(button_door)

panel = Panel(Vector((27, 13)))
panel_door1 = VerticalDoor(Vector((26, 16)))
panel_door2 = VerticalDoor(Vector((24, 16)))
panel_door3 = VerticalDoor(Vector((28, 16)))
panel.add_contact(panel_door1)
panel.add_contact(panel_door2)
panel.add_contact(panel_door3)
panel_lever = Lever(Vector((26, 10)))
panel_lever.add_contact(panel)

loose_panel = LoosePanel(Vector((25, 3)))
loose_panel_door1 = VerticalDoor(Vector((24, 6)))
loose_panel_door2 = VerticalDoor(Vector((22, 6)))
loose_panel_door3 = VerticalDoor(Vector((26, 6)))
loose_panel.add_contact(loose_panel_door1)
loose_panel.add_contact(loose_panel_door2)
loose_panel.add_contact(loose_panel_door3)

lever2 = Lever(Vector((23, 29)))
timed_door1 = VerticalTimedDoor(Vector((25, 27)))
timed_door2 = VerticalTimedDoor(Vector((27, 27)))
timed_door1.set_timer(3)
timed_door2.set_timer(5)
lever2.add_contact(timed_door1)
lever2.add_contact(timed_door2)

lever3 = Lever(Vector((27, 21)))
timed_door3 = HorizontalTimedDoor(Vector((23, 25)))
timed_door4 = HorizontalTimedDoor(Vector((23, 23)))
timed_door3.set_timer(3)
timed_door4.set_timer(5)
lever3.add_contact(timed_door3)
lever3.add_contact(timed_door4)

scientist = Scientist(Vector((17, 11)))
scientist.set_patrol(Vector((17, 7)))

missile_launcher = MissileLauncher(Vector((17, 16)))

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
"""

# level.save("../assets/level.txt")
# level.load_level("../assets/level.txt")