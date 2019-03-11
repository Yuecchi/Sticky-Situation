try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import game
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

testsprite = simplegui._load_local_image('../assets/testsprite.png')
testblock = simplegui._load_local_image('../assets/testblock.png')
horse = simplegui._load_local_image('../assets/SS_Horse_1.1.png')
testlever = simplegui._load_local_image('../assets/lever.png')
testdoor = simplegui._load_local_image('../assets/door.png')
testbutton = simplegui._load_local_image('../assets/button.png')
test_panel = simplegui._load_local_image('../assets/panel.png')
test_loose_panel = simplegui._load_local_image('../assets/loose_panel.png')

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

        # save tilemap
        file.write("MAP_START\n")
        for y in range(len(self.tilemap.map)):
            buffer = str(self.tilemap.map[y]).strip("[]").replace(" ", "") + "\n"
            file.write(buffer)
        file.write("MAP_END\n")

        # save entities
        file.write("ENTITIES_START\n")
        for entity in Entity.entities:
            buffer = entity.save_data() + "\n"
            file.write(buffer)
        file.write("ENTITIES_END\n")

        # save contacts
        file.write("CONTACTS_START\n")
        for entity in Entity.entities:
            buffer = entity.contact_data()
            if buffer:
                file.write(buffer + "\n")
        file.write("CONTACTS_END\n")

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

    # create a new tilemap
    tilemap = Tilemap(tilesheet, map)

    # create level and load it as the games current level
    level = Level(tilemap)
    game._game.change_level(level)

    # load entities
    Entity.entities = []

    # retrieve entity data and create entities
    for line in file:
        buffer = line.strip("\n")
        if buffer == "ENTITIES_START":
            continue
        elif buffer == "ENTITIES_END":
            break

        data = list_csv(buffer)
        if data[0] == Player.ENTITY_TYPE:
            Player(Vector((data[1], data[2])), horse)
        elif data[0] == PushBlock.ENTITY_TYPE:
            PushBlock(Vector((data[1], data[2])), testblock)
        elif data[0] == Lever.ENTITY_TYPE:
            Lever(Vector((data[1], data[2])), testlever)
        elif data[0] == Button.ENTITY_TYPE:
            Button(Vector((data[1], data[2])), testbutton)
        elif data[0] == Panel.ENTITY_TYPE:
            Panel(Vector((data[1], data[2])), test_panel)
        elif data[0] == LoosePanel.ENTITY_TYPE:
            LoosePanel(Vector((data[1], data[2])), test_loose_panel)
        elif data[0] == Door.ENTITY_TYPE:
            Door(Vector((data[1], data[2])), testdoor)


    # retrieve contact data and set contacts
    for line in file:
        buffer = line.strip("\n")
        if buffer == "CONTACTS_START":
            continue
        elif buffer == "CONTACTS_END":
            break

        data = list_csv(buffer)
        Entity.entities[data[0] - 1].set_contact(Entity.entities[data[1] - 1])
        if len(data) == 3:
            Entity.entities[data[0] - 1].set_timer(data[2])

    # aset player as camera anchor and store default map state
    game._game.camera.set_anchor(Entity.entities[0])
    game._game.level.store_reset_maps()

    # close the level file
    file.close()