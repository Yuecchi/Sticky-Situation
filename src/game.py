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

    TITLE     = 1
    GAME      = 2
    GAME_OVER = 3
    PAUSE     = 4
    EDITOR    = 5

class StaticImage:

    def __init__(self, img):

        self.img = img
        self.dims = (img.get_width(), img.get_height())
        self.src_pos = (self.dims[0] /  2, self.dims[1] / 2)

    def draw(self, canvas, pos):
        canvas.draw_image(self.img, self.src_pos, self.dims, pos, self.dims)

class Game:

    TITLE_BG_SRC = simplegui._load_local_image("../assets/menus/title_menu/title_background.png")
    TITLE_BG = StaticImage(TITLE_BG_SRC)

    LIVES_ICON_SRC = simplegui._load_local_image("../assets/ui/lives_icon_16x16.png")
    LIVES_ICON = StaticImage(LIVES_ICON_SRC)

    PAUSE_BG_SRC = simplegui._load_local_image("../assets/menus/pause_menu/pause_background.png")
    PAUSE_BG = StaticImage(PAUSE_BG_SRC)

    DEATH_IMG_SRC = simplegui._load_local_image('../assets/ui/death.png')
    DEATH_IMG = StaticImage(DEATH_IMG_SRC)

    GAME_OVER_IMG_SRC = simplegui._load_local_image('../assets/ui/game_over.png')
    GAME_OVER_IMG = StaticImage(GAME_OVER_IMG_SRC)

    def __init__(self):

        self.state = GameState.TITLE
        self.level = None
        self.clock = Clock()
        self.camera = Camera()

        self.lives = 0
        self.score = 0
        self.time  = 0 # time will be loaded from level I guess

        self.mouse = handlers.mouse
        self.title_menu = menu.title_menu
        self.pause_menu = menu.pause_menu

    def start(self):
        self.lives = 3
        self.score = 0
        self.time  = 999 * 60 #todo: temporary time setter for testing
        level.load_level("../assets/levels/elliot.txt")
        self.change_state(GameState.GAME)

    def launch_editor(self):
        self.change_state(GameState.EDITOR)

    def initialize_title_menu(self):
        self.title_menu.options[0].set_action(self.start)
        self.title_menu.options[1].set_action(self.launch_editor) #todo: goto editor
        self.title_menu.options[2].set_action(exit)

    def unpause(self):
        self.change_state(GameState.GAME)

    def retry(self):
        self.change_state(GameState.GAME)
        Entity.entities[0].kill()

    def back_to_title(self):
        self.change_state(GameState.GAME_OVER)

    def initialize_pause_menu(self):
        self.pause_menu.options[0].set_action(self.unpause)
        self.pause_menu.options[1].set_action(self.retry)
        self.pause_menu.options[2].set_action(self.back_to_title)

    def change_state(self, state):
        self.state = state

    def change_level(self, level):
        self.level = level
        self.camera.set_max_scroll(self.level.tilemap)

    def draw(self, canvas):

        if self.state == GameState.TITLE:

            # display tile screen background image
            Game.TITLE_BG.draw(canvas, (FRAMEWIDTH / 2, FRAMEHEIGHT / 2))

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

            # display ui
            canvas.draw_text("x " + str(self.lives), (32, 20), 16, "lime", "monospace")
            canvas.draw_text("score: " + str(self.score), (280, 20), 16, "lime", "monospace")
            canvas.draw_text("time: " + str(self.time // 60), (520, 20), 16, "lime", "monospace")
            Game.LIVES_ICON.draw(canvas, (16, 16))

            # draw death overlay when neeeded
            if Entity.entities[0].dead:
                if self.lives > 0:
                    Game.DEATH_IMG.draw(canvas, (FRAMEWIDTH / 2, FRAMEHEIGHT / 2))
                else:
                    Game.GAME_OVER_IMG.draw(canvas, (FRAMEWIDTH / 2, FRAMEHEIGHT / 2))

            # pause functionality
            if handlers.keyboard.p:
                self.change_state(GameState.PAUSE)
                handlers.keyboard.p = False

            # game over
            if self.state == GameState.GAME_OVER:
                self.level = None
                self.change_state(GameState.TITLE)
                self.title_menu.options[0].selected = False

        if self.state == GameState.PAUSE:

            # check for pause menu interaction
            self.pause_menu.update(self.mouse)

            # if the game is paused, draw but don't update
            self.level.tilemap.draw(canvas)

            for entity in Entity.entity_drawing[::-1]:
                entity.draw(canvas)

            for projectile in Projectile.projectiles:
                projectile.draw(canvas)

            # display ui
            #todo: will need to change shit here that happens up there
            # turns out being lazy before creates more work now...WHO KNEW!??
            canvas.draw_text("x " + str(self.lives), (32, 20), 16, "lime", "monospace")
            Game.LIVES_ICON.draw(canvas, (16, 16))

            #draw menu overlay
            Game.PAUSE_BG.draw(canvas, (FRAMEWIDTH / 2, FRAMEHEIGHT / 2))
            self.pause_menu.display(canvas)

            # unpause functionality
            if handlers.keyboard.p:
                self.change_state(GameState.GAME)
                handlers.keyboard.p = False

            # game over
            if self.state == GameState.GAME_OVER:
                self.level = None
                self.change_state(GameState.TITLE)
                self.title_menu.options[0].selected = False

        if self.state == GameState.EDITOR:
            # initialize editor
            pass
        """
        canvas.draw_text("player position: " + str(player.pos), (0, 16), 16, "White")
        canvas.draw_text("player direction: " + str(player.direction), (0, 32), 16, "White")
        canvas.draw_text("player state: " + str(player.state), (0, 48), 16, "White")
        
        
        for i in range(len(self.level.entitymap)):
            canvas.draw_text(str(self.level.entitymap[i]), (0, 16 + (i * 16)), 16, "White")
        """

        self.mouse.reset()
        if self.state != GameState.PAUSE:
            self.clock.tick()
            if self.time > 0:
                self.time -= 1

_game = Game()
_game.initialize_title_menu()
_game.initialize_pause_menu()

"""
CANVAS_DIMS = [900, 600]
editor_frame = simplegui.create_frame("LevelEditor", CANVAS_DIMS[0], CANVAS_DIMS[1])

editor_frame.set_mouseclick_handler(levelEditor.click)
editor_frame.set_keydown_handler(levelEditor.key_down)
editor_frame.set_mousedrag_handler(levelEditor.drag)

impFile = editor_frame.add_input("Load: Level Name", levelEditor.load, 100)
expFile = editor_frame.add_input("Save: Level Name", levelEditor.save, 100)

changeDims = editor_frame.add_input("Resize: (Width, Height)", levelEditor.resize, 100)
addTimer = editor_frame.add_input("Add Timer: Time (s)", levelEditor.add_timer, 100)

editor_frame.set_draw_handler(levelEditor.draw)
"""
