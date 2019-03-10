try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from vectors import Vector
from entities import Entity
from tileEngine import TileType

class Level:

    def __init__(self, tilemap, entitymap):

        self.tilemap = tilemap
        self.entitymap = entitymap
        self.spawn = Vector((0, 0))

        self.reset_tilemap = [
            [
                0 for x in range(len(self.entitymap[0]))
            ] for y in range(len(self.entitymap))
        ]

        self.reset_entitymap = [
            [
                0 for x in range(len(self.entitymap[0]))
            ] for y in range(len(self.entitymap))
        ]

        self.closed_pit = None
        for i in range(len(self.tilemap.tilesheet.tiles)):
            if self.tilemap.tilesheet.tiles[i].type == TileType.CLOSED_PIT:
                self.closed_pit = i
                break


    def set_spawn(self, pos):
        self.spawn = pos

    def store_entities(self):
        pass

    def store_reset_maps(self):
        for y in range(len(self.reset_tilemap)):
            for x in range(len(self.reset_tilemap[0])):
                self.reset_tilemap[y][x]  =  self.tilemap.map[y][x]
                self.reset_entitymap[y][x] = self.entitymap[y][x]

    def reset_level(self):
        for y in range(len(self.reset_tilemap)):
            for x in range(len(self.reset_tilemap[0])):
                self.tilemap.map[y][x] = self.reset_tilemap[y][x]
                self.entitymap[y][x] = self.reset_entitymap[y][x]

        for entity in Entity.entities:
            entity.reset()

    def load_level(self, level):
        # TODO: will be able to load levels via external files
        pass

