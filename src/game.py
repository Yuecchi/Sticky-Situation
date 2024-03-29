try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from enum import IntEnum
from vectors import Vector
from tileEngine import Tilesheet
from tileEngine import Tilemap
from tileEngine import Tile
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

# canvas width and height
FRAMEWIDTH, FRAMEHEIGHT = 640, 480

# class for keeping track of the number of frames which have pass
# this is used for regulating sprite animation speeds
class Clock:

    def __init__(self):
        self.t = 0 # keeps track of the number of frames which have been processed since the program was launched

    # method which increments the frame count (this is to be called on each program loop)
    def tick(self):
        self.t += 1

    # method for regulating the speed of processes within the game
    # any processing which happens within the game can be throttled to
    # only happen every 'x' number of frames according to the 'rate' which is
    # passed to this function
    def transition(self, rate):
        return not(self.t % rate)

    # sets the number of frames which have been processed to zero
    def reset(self):
        self.t = 0

# enum for storing game states
# game states are using to keep track of which group of actions
# the game shpould currently be performing
class GameState(IntEnum):

    TITLE          = 1
    GAME           = 2
    GAME_OVER      = 3
    PAUSE          = 4
    EDITOR         = 5
    LEVEL_COMPLETE = 6

# class for storing static images and drawing with less hassle
class StaticImage:

    def __init__(self, img):

        self.img = img # source file for the static image
        self.dims = (img.get_width(), img.get_height()) # dimensions of the sources image file
        self.src_pos = (self.dims[0] /  2, self.dims[1] / 2) # center position of the source image

    # draws the source image unscaled at a given target position
    def draw(self, canvas, pos):
        canvas.draw_image(self.img, self.src_pos, self.dims, pos, self.dims)

# the game class holds several of the games multimedia resources ,it keeps track of the current game state
# and when gameplay is active, keeps track of the current level
class Game:

    # SEVERAL GRAPHICS AND MUSIC FILES USED EITHER IN GAME OR IN THE TITLE SCREEN MENU / PAUSE MENU
    TITLE_BG_SRC = simplegui._load_local_image("../assets/menus/title_menu/title_background.png")
    TITLE_BG = StaticImage(TITLE_BG_SRC)

    # the special hidden title screen image
    SANS_BG_SRC = simplegui._load_local_image("../assets/menus/title_menu/title_ness_background.png")
    SANS_BG = StaticImage(SANS_BG_SRC)

    # the ui "heart" sprite, displayed next to the number of lives the player current has left
    LIVES_ICON_SRC = simplegui._load_local_image("../assets/sprite_sheets/entities.png")
    LIVES_ICON = Tile(LIVES_ICON_SRC, [0, 27], [3, 27], True, 0, 15)

    # the pause menus creen background
    PAUSE_BG_SRC = simplegui._load_local_image("../assets/menus/pause_menu/pause_background.png")
    PAUSE_BG = StaticImage(PAUSE_BG_SRC)

    # the "you died" screen
    DEATH_IMG_SRC = simplegui._load_local_image('../assets/ui/death.png')
    DEATH_IMG = StaticImage(DEATH_IMG_SRC)

    # the game over screen
    GAME_OVER_IMG_SRC = simplegui._load_local_image('../assets/ui/game_over.png')
    GAME_OVER_IMG = StaticImage(GAME_OVER_IMG_SRC)

    # music to be played on the titile screen
    TITLE_MUSIC = simplegui._load_local_sound("../assets/menus/title_menu/SS_Original.ogg")

    # images to be displayed upon completion of each of the games levels
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

    # music to be played in levels
    MUSIC = (
        simplegui._load_local_sound("../assets/levels/music/beethoven.ogg"),
        simplegui._load_local_sound("../assets/levels/music/carmina.ogg"),
        simplegui._load_local_sound("../assets/levels/music/holst.ogg"),
        simplegui._load_local_sound("../assets/levels/music/toccata.ogg"),
        simplegui._load_local_sound("../assets/levels/music/china.ogg"),
        simplegui._load_local_sound("../assets/levels/music/strauss.ogg"),
        simplegui._load_local_sound("../assets/levels/music/rossini.ogg"),
        simplegui._load_local_sound("../assets/levels/music/brahms.ogg"),
    )

    def __init__(self):

        self.state = GameState.TITLE # stores the current game state
        self.level = None # store the currently active level
        self.clock = Clock() # a ticker used for regulating animations
        self.camera = Camera() # in game camera used for scrolling accross maps larger than the canvas size

        self.lives = 0 # the current number of lives the player has
        self.score = 0 # the players current score
        self.time  = 0 # the current time left to complete a level (to gain points from the level upon completion)
        self.editor_level = "_default" # the current loaded inside the level editor

        self.win_quote = 0 # the win quote to be displayed upon level completion

        self.mouse = handlers.mouse # the in game mouse
        self.title_menu = menu.title_menu # stores the functional units of the title screen
        self.pause_menu = menu.pause_menu # stores the functional units of the pause menu
        self.sans = False # keeps track of which tile screen image to display (normal or secret)

        self.close = True # a flag to determine when the program should close

        # a flag which indicates whether the game is being played in the main game
        # or in the level editors sandbox level player
        self.inSandbox = False
        self.music = None # stores the current music being played for a level

    # method which initializes a new game. It resets the players lives to the maximum,
    # resets the score, resets the timer for the level, loads the first level of the game
    # set the game state to "Game" so the level will be drawn and updated, and chooses a
    # random, piece of music from the song list to be played
    def start(self):
        self.lives = 100
        self.score = 0
        self.time  = 300 * 60  # todo: temporary time setter for testing
        level.load_level("../assets/levels/official/_jebaited.txt")
        self.change_state(GameState.GAME)
        self.music = Game.MUSIC[randint(0, len(Game.MUSIC) - 1)]

    # method which prepares the next level after a level have been completed
    # behave slightly differently in sandbox mode
    def next_level(self):

        # calculates the players score based on the amount of time
        # remainaing from the previous level
        self.score += (self.time // 60)

        # resets the level timer
        self.time = 300 * 60

        # if in sandbox mode, this will take you back to the editor
        if self.inSandbox:
            self.inSandbox = False
            self.change_state(GameState.EDITOR)
        elif self.level.next_level == '':
            # if there is no next level, the player is sent back to the title screen
            self.music.rewind()
            self.change_state(GameState.TITLE)
        else:
            # loads the next level and chooses a new song to play
            level.load_level(self.level.next_level)
            self.music.rewind()
            self.music = Game.MUSIC[randint(0, len(Game.MUSIC) - 1)]
            self.change_state(GameState.GAME)

    # switches to the level editor
    def launch_editor(self):
        self.change_state(GameState.EDITOR)

    # opens a level in sandbox mode. The number of lives is lower
    # and there is a flag set to true, indiciating that the game is
    # being played ins andbox mode
    def launch_sandbox(self):
        self.lives = 10
        self.score = 0
        self.time  = 300 * 60 # todo: temporary time setter for testing COPIED
        level.load_level("../assets/levels/" + self.editor_level + ".txt")
        self.inSandbox = True
        self.change_state(GameState.GAME)

    # attaches the title screens menu options to the tile menu
    def initialize_title_menu(self):
        self.title_menu.options[0].set_action(self.start)
        self.title_menu.options[1].set_action(self.launch_editor)
        self.title_menu.options[2].set_action(exit)

    # unpauses the game
    def unpause(self):
        self.change_state(GameState.GAME)

    # resets the current level
    def retry(self):
        self.change_state(GameState.GAME)
        Entity.entities[0].kill()

    # quits out of the current level back to the titile screen
    def back_to_title(self):
        self.change_state(GameState.GAME_OVER)

    # attaches the pause menu options to the pause menu
    def initialize_pause_menu(self):
        self.pause_menu.options[0].set_action(self.unpause)
        self.pause_menu.options[1].set_action(self.retry)
        self.pause_menu.options[2].set_action(self.back_to_title)

    # changes the current game state to a given state
    def change_state(self, state):
        self.state = state

    # changes the current level, to a given level
    # and determines the max scroll distance for the camera
    # for that level
    def change_level(self, level):
        self.level = level
        self.camera.set_max_scroll(self.level.tilemap)

    # the main game loop/ all drawing and game logic updates (besides those done in the level editor)
    # are called here
    def draw(self, canvas):

        global frame

        # the title screen game state, displays the title menu and allows the user
        # to exit the program, start a new game, or access the level editor
        if self.state == GameState.TITLE:
            Game.TITLE_MUSIC.play()
            # display tile screen background image
            if handlers.keyboard.p:
                self.sans = not self.sans
                handlers.keyboard.p = False

            # determines which title screen background image to display
            if self.sans:
                Game.SANS_BG.draw(canvas, (FRAMEWIDTH / 2, FRAMEHEIGHT / 2))
            else:
                Game.TITLE_BG.draw(canvas, (FRAMEWIDTH / 2, FRAMEHEIGHT / 2))

            # check for menu option interaction
            self.title_menu.update(self.mouse)

            # display title menu options
            self.title_menu.display(canvas)

            # if the game switches state away from title, the music for the
            # title screen is stopped
            if self.state != GameState.TITLE:
                Game.TITLE_MUSIC.rewind()

        # the main game state, allows the player to play levels in the game
        if self.state == GameState.GAME:

            # if a level is being played in sandbox mode, there is no music
            if not self.inSandbox:
                self.music.play()

            # update shit here (player pos, ai scripts, blah blah blah
            for entity in Entity.entity_updates:
                entity.update()

            # updates the logic for any projectiles which are currently active
            for projectile in Projectile.projectiles:
                projectile.update()

            # moves the camera according to the location of the anchor ( which is always the player)
            if self.camera.anchor:
                self.camera.update()

            # draws the level
            self.level.tilemap.draw(canvas)

            # draw all entities in the level (player, enimies, triggers etc)
            for entity in Entity.entity_drawing[::-1]:
                entity.draw(canvas)

            # draws all currently active projectiles in the level
            for projectile in Projectile.projectiles:
                projectile.draw(canvas)

            # display ui
            canvas.draw_text("x " + str(self.lives), (32, 20), 16, "lime", "monospace")
            canvas.draw_text("SCORE: " + str(self.score), (280, 20), 16, "lime", "monospace")
            canvas.draw_text("TIME: " + str(self.time // 60), (520, 20), 16, "lime", "monospace")

            # draws the games "lives" ui icon
            Game.LIVES_ICON.draw(canvas, 16, 16)

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

        # the pause state, allows for in game pauses and brings up a menu which allows
        # the player to return to gameplay, restart the current level, or quit back to the
        # main menu
        if self.state == GameState.PAUSE:

            # no music is played when in sandbox mode
            if not self.inSandbox:
                self.music.play()

            # check for pause menu interaction
            self.pause_menu.update(self.mouse)

            # if the game is paused, draw but don't update
            self.level.tilemap.draw(canvas)

            # draws the levels entities
            for entity in Entity.entity_drawing[::-1]:
                entity.draw(canvas)

            # draws any currently active projectiles
            for projectile in Projectile.projectiles:
                projectile.draw(canvas)

            # display ui
            # todo: will need to change shit here that happens up there
            # turns out being lazy before creates more work now...WHO KNEW!??
            # comment convos ftw
            canvas.draw_text("x " + str(self.lives), (32, 20), 16, "lime", "monospace")
            Game.LIVES_ICON.draw(canvas, 16, 16)

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
                # draws the current win quote upon completion of a level
                Game.YOU_WIN_IMG[self.win_quote].draw(canvas, (FRAMEWIDTH / 2, FRAMEHEIGHT / 2))
                if self.level.next_level == '':
                    # display the message for beating the game
                    canvas.draw_text("Congratulations, you Won! Press the action button to return to the title screen", (4, 460), 14, "Lime", "monospace")
                else:
                    # displays the level for beating a level
                    canvas.draw_text("Level Complete, Press the action button ('m') to proceed to the next level", (30, 460), 14, "Lime", "monospace")
                # proceeds to thge next level when the action button is pressed
                if handlers.keyboard.m == True:
                    self.next_level()
            else:
                self.next_level()

        # reset the mouse
        self.mouse.reset()
        if self.state != GameState.PAUSE:
            self.clock.tick()
            Game.LIVES_ICON.updated = False
            if self.time > 0:
                self.time -= 1

# FUCK YEAH
# grabs the frame from the main module
# this is part of how it is possible to switch between two frames
editor_frame = None
frame = None
def get_frame(f):

    global frame
    frame = f

# initializes the game
_game = Game()
_game.initialize_title_menu()
_game.initialize_pause_menu()



