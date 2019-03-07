try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

class Level:

    def __init__(self, tilemap, entitymap):

        self.tilemap = tilemap
        self.entitymap = entitymap

    def load_level(self, level):
        # TODO: will be able to load levels via external files
        pass

