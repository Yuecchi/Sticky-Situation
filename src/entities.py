# from gfx import Sprite

class Entity:

    def __init__(self, pos):
        self.pos = pos

class Player(Entity):

    def __init__(self, pos):
        Entity.__init__(self, pos)
