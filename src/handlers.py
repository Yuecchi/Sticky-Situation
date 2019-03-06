try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import game
from vectors import Vector

class keyboard:

    def __init__(self):
        pass


def keyup(key):
    pass

def keydown(key):

    if key == simplegui.KEY_MAP['w']:
        game.player.move(game.player.pos + Vector((0, -1)))
    if key == simplegui.KEY_MAP['a']:
        game.player.move(game.player.pos + Vector((-1, 0)))
    if key == simplegui.KEY_MAP['s']:
        game.player.move(game.player.pos + Vector((0, 1)))
    if key == simplegui.KEY_MAP['d']:
        game.player.move(game.player.pos + Vector((1, 0)))
