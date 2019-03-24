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
from random import randint

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

    TITLE          = 1
    GAME           = 2
    GAME_OVER      = 3
    PAUSE          = 4
    EDITOR         = 5
    LEVEL_COMPLETE = 6

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

    TITLE_MUSIC = simplegui._load_local_sound("../assets/menus/title_menu/SS_Original.wav")

    YOU_WIN_IMG_SRC = (
        simplegui._load_local_image('../assets/ui/SS-win-1.png'),
        simplegui._load_local_image('../assets/ui/SS-win-2.png'),
        simplegui._load_local_image('../assets/ui/SS-win-3.png'),
        simplegui._load_local_image('../assets/ui/SS-win-4.png'),
        simplegui._load_local_image('../assets/ui/SS-win-6.png'),
        simplegui._load_local_image('../assets/ui/SS-win-8.png'),
        simplegui._load_local_image('../assets/ui/SS-win-9.png'),
    )

    YOU_WIN_IMG = (
        StaticImage(YOU_WIN_IMG_SRC[0]),
        StaticImage(YOU_WIN_IMG_SRC[1]),
        StaticImage(YOU_WIN_IMG_SRC[2]),
        StaticImage(YOU_WIN_IMG_SRC[3]),
        StaticImage(YOU_WIN_IMG_SRC[4]),
        StaticImage(YOU_WIN_IMG_SRC[5]),
        StaticImage(YOU_WIN_IMG_SRC[6]),
    )

    MUSIC = (
        simplegui._load_local_sound("../assets/levels/music/bald.ogg"),
        simplegui._load_local_sound("../assets/levels/music/beethoven.ogg"),
        simplegui._load_local_sound("../assets/levels/music/carmina.ogg"),
        simplegui._load_local_sound("../assets/levels/music/holst.ogg"),
        simplegui._load_local_sound("../assets/levels/music/toccata.ogg"),
        simplegui._load_local_sound("../assets/levels/music/valkyrie.ogg")
    )

    def __init__(self):

        self.state = GameState.TITLE
        self.level = None
        self.clock = Clock()
        self.camera = Camera()

        self.lives = 0
        self.score = 0
        self.time  = 0 # time will be loaded from level I guess

        self.win_quote = 0

        self.mouse = handlers.mouse
        self.title_menu = menu.title_menu
        self.pause_menu = menu.pause_menu

        self.close = True

        self.inSandbox = False
        self.music = None

    def start(self):
        self.lives = 100
        self.score = 0
        self.time  = 300 * 60 #todo: temporary time setter for testing
        level.load_level("../assets/levels/_level1.txt")
        self.change_state(GameState.GAME)
        self.music = Game.MUSIC[randint(0, 5)]

    def next_level(self):
        self.score += (self.time // 60)
        self.time = 300 * 60

        if self.inSandbox:
            self.inSandbox = False
            self.change_state(GameState.EDITOR)
        elif self.level.next_level == '':
            self.music.rewind()
            self.change_state(GameState.TITLE)
        else:
            level.load_level(self.level.next_level)
            self.music.rewind()
            self.music = Game.MUSIC[randint(0, 5)]
            self.change_state(GameState.GAME)

    def launch_editor(self):
        self.change_state(GameState.EDITOR)

    def launch_sandbox(self, level_name):
        self.lives = 10
        self.score = 0
        self.time  = 300 * 60 #todo: temporary time setter for testing COPIED
        level.load_level("../assets/levels/" + level_name + ".txt")
        self.inSandbox = True
        self.change_state(GameState.GAME)

    def initialize_title_menu(self):
        self.title_menu.options[0].set_action(self.start)
        self.title_menu.options[1].set_action(self.launch_editor)
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

        global frame

        if self.state == GameState.TITLE:
            Game.TITLE_MUSIC.play()
            # display tile screen background image
            Game.TITLE_BG.draw(canvas, (FRAMEWIDTH / 2, FRAMEHEIGHT / 2))

            # check for menu option interaction
            self.title_menu.update(self.mouse)

            # display title menu options
            self.title_menu.display(canvas)

            if self.state != GameState.TITLE:
                Game.TITLE_MUSIC.rewind()

        if self.state == GameState.GAME:

            if not self.inSandbox:
                self.music.play()

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
                if self.inSandbox:
                    self.inSandbox = False
                    self.change_state(GameState.EDITOR)
                else:
                    self.music.rewind()
                    self.change_state(GameState.TITLE)


        if self.state == GameState.PAUSE:

            if not self.inSandbox:
                self.music.play()

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
                if self.inSandbox:
                    self.inSandbox = False
                    self.change_state(GameState.EDITOR)
                else:
                    self.music.rewind()
                    self.change_state(GameState.TITLE)

        if self.state == GameState.EDITOR:
            self.close = False
            frame.stop()

        # level complete
        if self.state == GameState.LEVEL_COMPLETE:
            if not self.inSandbox:
                Game.YOU_WIN_IMG[self.win_quote].draw(canvas, (FRAMEWIDTH / 2, FRAMEHEIGHT / 2))
                canvas.draw_text("Level Complete, Press the action button ('m') to proceed to the next level", (30, 460), 14, "Lime", "monospace")
                if handlers.keyboard.m == True:
                    self.next_level()
            else:
                self.next_level()

        self.mouse.reset()
        if self.state != GameState.PAUSE:
            self.clock.tick()
            if self.time > 0:
                self.time -= 1

# FUCK YEAH
editor_frame = None
frame = None
def get_frame(f):

    global frame
    frame = f

_game = Game()
_game.initialize_title_menu()
_game.initialize_pause_menu()



