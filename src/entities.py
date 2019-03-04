try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import gfx

class Entity:

    def __init__(self, pos):
        self.pos = pos

class Player(Entity):

    def __init__(self, pos):
        Entity.__init__(self, pos)