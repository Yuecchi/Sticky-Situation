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
from entities   import VerticalDoor
from entities   import HorizontalDoor
from entities   import VerticalTimedDoor
from entities   import HorizontalTimedDoor
from entities   import Scientist
from entities   import ScientistState
from entities   import MissileLauncher
import tileEngine
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

        # todo: need to save multiple contacts
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

    tilesheet_path = file.readline().strip("\n")
    tilesheet = tileEngine.load_tilesheet(tilesheet_path)

    """
    # read source image path
    img_path = file.readline().strip("\n")

    # read animation frame, types and animation speed index
    # data and store them as individual lists
    for i in range(3):
        buffer = file.readline().strip("\n")
        index.append(list_csv(buffer))

    # create new tilesheet
    tilesheet = Tilesheet(img_path, index[0], index[1], index[2])
    """

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
    entity_index = 0
    for line in file:
        buffer = line.strip("\n")
        if buffer == "ENTITIES_START":
            continue
        elif buffer == "ENTITIES_END":
            break

        data = list_csv(buffer)
        if data[0] == Player.ENTITY_TYPE: # 1
            Player(Vector((data[1], data[2])))
        elif data[0] == PushBlock.ENTITY_TYPE: # 2
            PushBlock(Vector((data[1], data[2])))
        elif data[0] == Lever.ENTITY_TYPE: # 3
            Lever(Vector((data[1], data[2])))
        elif data[0] == Button.ENTITY_TYPE: # requires timer data
            Button(Vector((data[1], data[2])))
            Entity.entities[entity_index].set_timer(data[3])
        elif data[0] == Panel.ENTITY_TYPE: # 5
            Panel(Vector((data[1], data[2])))
        elif data[0] == LoosePanel.ENTITY_TYPE: # 6
            LoosePanel(Vector((data[1], data[2])))
        elif data[0] == VerticalDoor.ENTITY_TYPE: # 7
            VerticalDoor(Vector((data[1], data[2])))
        elif data[0] == HorizontalDoor.ENTITY_TYPE: # 8
            HorizontalDoor(Vector((data[1], data[2])))
        elif data[0] == VerticalTimedDoor.ENTITY_TYPE: # 9 requires timer data
            VerticalTimedDoor(Vector((data[1], data[2])))
            Entity.entities[entity_index].set_timer(data[3])
        elif data[0] == HorizontalTimedDoor.ENTITY_TYPE: # 10 requires timer data
            HorizontalTimedDoor(Vector((data[1], data[2])))
            Entity.entities[entity_index].set_timer(data[3])
        elif data[0] == Scientist.ENTITY_TYPE: # 11 requires patrol point
            Scientist(Vector((data[1], data[2])))
            Entity.entities[entity_index].set_patrol(Vector((data[3], data[4])))
        elif data[0] == MissileLauncher.ENTITY_TYPE: # requires range and fuse
            MissileLauncher(Vector((data[1], data[2])))
            Entity.entities[entity_index].set_range(data[3])
            Entity.entities[entity_index].set_fuse(data[4])

        entity_index += 1

    # retrieve contact data and set contacts
    for line in file:
        buffer = line.strip("\n")
        if buffer == "CONTACTS_START":
            continue
        elif buffer == "CONTACTS_END":
            break
            
        data = list_csv(buffer)

        if Entity.entities[data[0] - 1].ENTITY_TYPE != Button.ENTITY_TYPE:
            Entity.entities[data[0] - 1].add_contact(Entity.entities[data[1] - 1])
        else:
            Entity.entities[data[0] - 1].set_contact(Entity.entities[data[1] - 1])

    # set player as camera anchor and store default map state
    game._game.camera.set_anchor(Entity.entities[0])
    game._game.level.store_reset_maps()

    # create specific entity order for updates and drawing
    temp = []
    for entity in Entity.entities:
        if entity.ENTITY_TYPE == PushBlock.ENTITY_TYPE:
            temp.append(entity)
        else:
            Entity.entity_updates.append(entity)
    Entity.entity_updates.extend(temp)

    temp = []
    for entity in Entity.entities:
        if entity.isTrigger:
            temp.append(entity)
        else:
            Entity.entity_drawing.append(entity)
    Entity.entity_drawing.extend(temp)

    # close the level file
    file.close()