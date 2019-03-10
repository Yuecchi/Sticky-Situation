try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from vectors import Vector
import entities
from entities   import Entity
from entities   import Player
from entities   import PlayerState
from entities   import PushBlock
from entities   import Lever
from entities   import Button
from entities   import Panel
from entities   import LoosePanel
from entities   import Door
from tileEngine import TileType
from tileEngine import Tilesheet
from tileEngine import Tilemap

class Level:

    def __init__(self, tilemap):

        self.tilemap = tilemap
        self.entitymap = [
            [
                0 for x in range(len(tilemap.map[0]))
            ] for y in range(len(tilemap.map))
        ]

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

    def save(self, path):
        file = open(path, "wt")

        # write tilesheet path
        buffer = self.tilemap.tilesheet.img_path + "\n"
        file.write(buffer)

        # write index data
        buffer = str(self.tilemap.tilesheet.index).strip("[]").replace(" ", "") + "\n"
        file.write(buffer)

        # write types data
        buffer = str(self.tilemap.tilesheet.types).strip("[]").replace(" ", "") + "\n"
        file.write(buffer)

        # write speeds data
        buffer = str(self.tilemap.tilesheet.speeds).strip("[]").replace(" ", "") + "\n"
        file.write(buffer)

        file.write("MAP_START\n")
        for y in range(len(self.tilemap.map)):
            buffer = str(self.tilemap.map[y]).strip("[]").replace(" ", "") + "\n"
            file.write(buffer)
        file.write("MAP_END\n")

        file.write("ENTITIES_START\n")
        for entity in Entity.entities:
            buffer = entity.save_data() + "\n"
            file.write(buffer)
        file.write("ENTITIES_END\n")

        file.close()

def list_csv(buffer):
    data = []
    val = ""
    for c in buffer:
        if c == ",":
            data.append(int(val))
            val = ""
        else:
            val += c
    data.append(int(val))
    return data

def load_level(path):

    # create an empty list to store the three indexes
    index = []

    # open the tilesheet file
    file = open(path, "rt")

    # read source image path
    img_path = file.readline().strip("\n")

    # read animation frame, types and animation speed index
    # data and store them as individual lists
    for i in range(3):
        buffer = file.readline().strip("\n")
        index.append(list_csv(buffer))

    # create new tilesheet
    tilesheet = Tilesheet(img_path, index[0], index[1], index[2])

    # create an empty list to store the map
    map = []

    for line in file:
        if line.strip("\n") == "MAP_START":
            continue
        elif line.strip("\n") == "MAP_END":
            break
        else:
            buffer = line.strip("\n")
            map.append(list_csv(buffer))

    # close the tilemap file
    file.close()

    # create a new tilemap
    tilemap = Tilemap(tilesheet, map)

    # return level
    return Level(Tilemap)
