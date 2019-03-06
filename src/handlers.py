try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import game
from vectors import Vector

class Keyboard:

    def __init__(self):

        self.w = False
        self.a = False
        self.s = False
        self.d = False

    def keydown(self, key):

        #TODO: PLAYER MOVEMENT IS CURRENTLY HACKED IN

        if key == simplegui.KEY_MAP['w']:
            game.player.move(game.player.pos + Vector((0, -1)))
            self.w = True
        if key == simplegui.KEY_MAP['a']:
            game.player.move(game.player.pos + Vector((-1, 0)))
            self.a = True
        if key == simplegui.KEY_MAP['s']:
            game.player.move(game.player.pos + Vector((0, 1)))
            self.s = True
        if key == simplegui.KEY_MAP['d']:
            game.player.move(game.player.pos + Vector((1, 0)))
            self.d = True

    def keyup(self, key):

        if key == simplegui.KEY_MAP['w']:
            self.w = False
        if key == simplegui.KEY_MAP['a']:
            self.a = False
        if key == simplegui.KEY_MAP['s']:
            self.s = False
        if key == simplegui.KEY_MAP['d']:
            self.d = False

keyboard = Keyboard()



