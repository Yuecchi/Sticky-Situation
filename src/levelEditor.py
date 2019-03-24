try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import game
import level
from tileEngine import Tile
from vectors import Vector

CANVAS_DIMS = [900, 600]
TILE_SIZE = 32

ENTITY_IMG = simplegui._load_local_image('../assets/sprite_sheets/entities.png')
ENTITY_SRC_POS = [(4.5*TILE_SIZE, 20.5*TILE_SIZE),  # Blank - 0
                  (0.5*TILE_SIZE, 18.5*TILE_SIZE),  # Player - 1
                  (13.5*TILE_SIZE, 18.5*TILE_SIZE),  # Block - 2
                  (0.5*TILE_SIZE, 19.5*TILE_SIZE),  # Lever - 3
                  (4.5*TILE_SIZE, 22.5*TILE_SIZE),  # Button - 4
                  (0.5*TILE_SIZE, 22.5*TILE_SIZE),  # Panel - 5
                  (2.5*TILE_SIZE, 22.5*TILE_SIZE),  # LoosePanel - 6
                  (0.5*TILE_SIZE, 24.5*TILE_SIZE),  # Door - 7
                  (5.5*TILE_SIZE, 24.5*TILE_SIZE),  # HorDoor - 8
                  (8.5*TILE_SIZE, 24.5*TILE_SIZE),  # Timed Door - 9
                  (12.5*TILE_SIZE, 24.5*TILE_SIZE),  # Timer HorDoor - 10
                  (15.5*TILE_SIZE, 14.5*TILE_SIZE),  # Scientist - 11
                  (0.5*TILE_SIZE, 20.5*TILE_SIZE)]  # Missile Launcher - 12
ENTITY_TRIGGER = [False, False, False, True, True, True, True, False, False, False, False, False, False]
ENTITY_TIMER = [None, None, None, None, 5, None, None, None, None, 5, 5, None, 5]
ENTITY_TARGET = [False, False, False, False, False, True, False, True, True, True, True, False, False]
ENTITY_OTHER = [None, None, None, None, None, None, None, None, None, None, None, [0, 0], [3]]
TILE_TYPE = ["EMPTY", "SOLID", "ICY", "LEFT_FENCE", "RIGHT_FENCE", "CONVEYOR_UP", "CONVEYOR_LEFT",
             "CONVEYOR_DOWN", "CONVEYOR_RIGHT", "SPIKES", "OPEN_PIT", "CLOSED_PIT", "GLUE", "UP_FENCE",
             "FIRE", "FAN", "WATER", "LASER", "GHOST", "GOAL"]

level_loaded = False

class SquareTile:
    def __init__(self, x, y, tile=True, id=-1):
        self.x = x
        self.y = y
        self.tileNo = id  # Change to selectNo or not?
        self.points = [(self.x, self.y),
                       (self.x + TILE_SIZE, self.y),
                       (self.x + TILE_SIZE, self.y + TILE_SIZE),
                       (self.x, self.y + TILE_SIZE)]
        self.tile = tile

    def paint(self, brush):
        self.tileNo = brush

    def shiftY(self, shift):
        self.y += shift
        self.points = [(self.x, self.y),
                       (self.x + TILE_SIZE, self.y),
                       (self.x + TILE_SIZE, self.y + TILE_SIZE),
                       (self.x, self.y + TILE_SIZE)]

    def draw(self, canvas):
        if self.tile:  # For tiles
            if self.tileNo == -1:
                return
            if isinstance(inputs.tile_sheet.tiles[self.tileNo], BigTile):
                big_in_use = inputs.tile_sheet.tiles[self.tileNo]
                for y in range(len(big_in_use.tiles)):
                    for x in range(len(big_in_use.tiles[0])):
                        inputs.tile_sheet.tiles[big_in_use.tiles[y][x]].draw(canvas, (TILE_SIZE / 2) + self.x +
                                                                             (x * TILE_SIZE), (TILE_SIZE / 2) +
                                                                             self.y + (y * TILE_SIZE))
            else:
                inputs.tile_sheet.tiles[self.tileNo].draw(canvas, (TILE_SIZE / 2) + self.x, (TILE_SIZE / 2) + self.y)
        else:  # For entities
            if self.tileNo == -1:
                return
            else:
                pos = ((TILE_SIZE/2) + self.x, (TILE_SIZE/2) + self.y)
                canvas.draw_image(ENTITY_IMG, ENTITY_SRC_POS[self.tileNo], (TILE_SIZE, TILE_SIZE), pos, (TILE_SIZE, TILE_SIZE))

class FakeEntity:
    def __init__(self, pos, type, time_in=-1, extra=[]):
        self.pos = pos
        self.type = type
        self.trigger = ENTITY_TRIGGER[type]
        self.target = ENTITY_TARGET[type]
        self.timer = time_in
        if time_in == -1:  # If no input timer given, assign default
            self.timer = ENTITY_TIMER[type]
        self.contacts = []
        self.extra = extra
        if len(extra) == 0:  # If no extra input given, assign default
            self.extra = ENTITY_OTHER[type]

    def addContact(self, contact):
        if contact not in self.contacts:
            self.contacts.append(contact)

    def changePos(self, new_pos):
        self.pos = new_pos

    def __eq__(self, other):
        if other is None:
            return False
        return self.pos == other.pos and self.type == other.type

    def remove(self):
        # Remove this entity from all contacts
        for entity in inputs.entities:
            if len(entity.contacts) != 0:
                for contact in entity.contacts:
                    if contact.__eq__(self):
                        if entity.__eq__(toolbar.entity):
                            toolbar.list.remove(self)
                        else:
                            entity.contacts.remove(self)
        inputs.entities.remove(self)  # Remove this entity

    def save_data(self):
        out = ""
        if self.type == 1:
            out += str(self.type) + "," + str(self.pos[1]) + "," + str(self.pos[0])
        else:
            out += str(self.type) + "," + str(self.pos[0]) + "," + str(self.pos[1])
        if self.extra is not None:
            for info in self.extra:
                out += "," + str(info)
        if self.timer is not None:
            out += "," + str(self.timer)
        return out

    def contact_data(self):
        string = ""
        if self.trigger != -1:
            for i in range(len(self.contacts)):
                id = inputs.entities.index(self)
                other_id = inputs.entities.index(self.contacts[i])
                if self.type == 4:
                    string += str(id+1) + "," + str(other_id+1) + "," + str(self.timer)
                else:
                    string += str(id+1) + "," + str(other_id+1)
                if i != len(self.contacts) - 1:
                    string += "\n"
        return string


class BigTile:  # Contains tiles with it, plus animated
    def __init__(self, tiles, tile_no):
        self.tiles = tiles
        self.tileNo = tile_no

    def contains(self, tile_no):
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                if self.tiles[y][x] == tile_no:
                    return True
        return False


# Like TileMap
class Grid:
    def __init__(self, cols=5, rows=5, x=50, y=50, view_frame = (2, 2), default=-1, tile=True, hidden=False, inactive=False, map=[]):
        self.hidden = hidden
        self.default = default
        self.isTile = tile
        self.inactive = inactive
        self.map = map  # Has indexes
        self.frame = view_frame  # To control viewable area
        self.frameStart = [0, 0]
        # Create the grid of tiles
        self.tiles = []  # Has tiles
        self.x = x
        self.y = y
        if len(self.map) == 0:
            self.cols = cols
            self.rows = rows
        else:
            self.cols = len(self.map[0])
            self.rows = len(self.map)
        temp_map = []
        for i in range(rows):
            current_row = []
            current_grid_row = []
            for j in range(cols):
                if len(self.map) == 0:  # Make it entity tile if entity grid
                    current_row.append(SquareTile(self.x + (TILE_SIZE * j), self.y + (TILE_SIZE * i), tile, default))
                    current_grid_row.append(default)
                else:  # If a map has been specified, use the indices there - won't be the case for entities
                    current_row.append(SquareTile(self.x + (TILE_SIZE * j), self.y + (TILE_SIZE * i), True, self.map[i][j]))

            self.tiles.append(current_row)
            if len(self.map) == 0:
                temp_map.append(current_grid_row)
        if len(self.map) == 0:
            self.map = temp_map

    def get_endpoint(self):
        return (self.tiles[self.frameStart[1] + self.frame[1] - 1][self.frameStart[0] + self.frame[0] - 1].x + TILE_SIZE,
                self.tiles[self.frameStart[1] + self.frame[1] - 1][self.frameStart[0] + self.frame[0] - 1].y + TILE_SIZE)

    def contains(self, pos):
        return self.x + TILE_SIZE*self.frameStart[0] < pos[0] < self.get_endpoint()[0] \
               and self.y + TILE_SIZE*self.frameStart[1] < pos[1] < self.get_endpoint()[1] \
               and not self.inactive

    def get_selected(self, pos, tile=True):
        x = (pos[0] - self.x) // TILE_SIZE
        y = (pos[1] - self.y) // TILE_SIZE

        if x < 0:
            x = 0
        elif x >= self.cols:
            x = self.cols - 1
        if y < 0:
            y = 0
        elif y >= self.rows:
            y = self.rows - 1

        if tile:
            return self.tiles[y][x]
        else:
            return [y, x]

    def in_selection(self, start, end, indexed=False):  # return a selection of tiles, no assumptions
        # take startPos and endPos to find tiles they correspond to
        tile_one = start
        tile_two = end
        # Sorting to make sure startSq is top left
        start_sq = [min(tile_one[0], tile_two[0]), min(tile_one[1], tile_two[1])]
        end_sq = [max(tile_one[0], tile_two[0]), max(tile_one[1], tile_two[1])]
        if indexed:
            return [start_sq, end_sq]
        selected = []
        for row in range(self.rows):
            for col in range(self.cols):
                if start_sq[0] <= row <= end_sq[0] and start_sq[1] <= col <= end_sq[1]:
                    selected.append(self.tiles[row][col])
        return selected

    def move_frame(self, x, y):
        if self.frameStart[0] + self.frame[0] + x <= self.cols and \
           self.frameStart[1] + self.frame[1] + y <= self.rows and \
           self.frameStart[0] + x >= 0 and self.frameStart[1] + y >= 0:
                self.frameStart[0] += x
                self.frameStart[1] += y
                for row in self.tiles:
                    for tile in row:
                        tile.x -= x * TILE_SIZE
                        tile.y -= y * TILE_SIZE
                self.x -= x * TILE_SIZE
                self.y -= y * TILE_SIZE
        else:
            if x > 0:
                self.move_frame(self.cols - (self.frameStart[0] + self.frame[0]), 0)
            elif x < 0:
                self.move_frame(-self.frameStart[0], 0)
            elif y > 0:
                self.move_frame(0, self.rows - (self.frameStart[1] + self.frame[1]))
            elif y < 0:
                self.move_frame(0, -self.frameStart[1])

    def resize(self, input_dims):
        if input_dims[0] < self.frame[0] or input_dims[1] < self.frame[1]:  # Can remove this
            return
        if self.rows != input_dims[1]:
            increment = -int((self.rows - input_dims[1]) / abs(self.rows - input_dims[1]))
            self.move_frame(-self.frameStart[0], -self.frameStart[1])
            while self.rows != input_dims[1]:
                if increment < 0:  # If more rows than wanted
                    self.tiles.pop()  # Pop last row
                elif increment > 0:
                    new_row = []
                    new_grid_row = []
                    for i in range(self.cols):
                        new_row.append(SquareTile(self.x + (TILE_SIZE * i), self.y + (TILE_SIZE * self.rows), self.isTile, self.default))
                        new_grid_row.append(self.default)
                    self.tiles.append(new_row)
                    self.map.append(new_grid_row)
                else:
                    break
                self.rows += increment

        if self.cols != input_dims[0]:
            increment = -int((self.cols - input_dims[0])/abs(self.cols - input_dims[0]))
            while self.cols != input_dims[0]:
                if increment < 0:  # If more cols than wanted
                    for i in range(self.rows):
                        self.tiles[i].pop()  # Pop last col
                elif increment > 0:
                    for i in range(self.rows):
                        self.tiles[i].append(SquareTile(self.x + (TILE_SIZE * self.cols), self.y + (TILE_SIZE * i), self.isTile, self.default))
                        self.map[i].append(self.default)
                else:
                    break
                self.cols += increment

        if toolbar.entity is not None:
            if len(level_entity_grid.tiles) <= toolbar.entity.pos[1] or \
                    len(level_entity_grid.tiles[0]) <= toolbar.entity.pos[0]:  # If outside bounds through resizing
                toolbar.entity = None
                toolbar.displayBox.tileNo = 0
                toolbar.extra_value = ""

    def draw(self, canvas):
        if not self.hidden:
            for y in range(self.frame[1]):
                if y + self.frameStart[1] < self.rows:
                    for x in range(self.frame[0]):
                        if x + self.frameStart[0] < self.cols:
                            self.tiles[y + self.frameStart[1]][x + self.frameStart[0]].draw(canvas)


class LevelTileSheet:
    # Use as you would the normal TileSheet but it has support for selecting and exporting big tiles
    def __init__(self, img_path, tile_index, tile_id_index, animation_speed_index):
        self.map = []
        self.img = simplegui._load_local_image(img_path)
        occupied = []
        for row in range(self.img.get_height() // 32):
            temp_row = []
            for col in range(self.img.get_width() // 32):
                temp_row.append(0)
            self.map.append(temp_row)
            occupied.append(temp_row.copy())

        # TileSheet.__init__(self, img, index) but fills a map in a nested loop
        self.imgPath = img_path
        self.tile_index = tile_id_index
        self.animation_index = animation_speed_index
        self.index = tile_index
        self.tiles = []
        self.cols = self.img.get_width() // 32
        start_index = [0, 0]
        end_index = [0, 0]
        index_i = 0
        self.tile_count = 0
        # Pass 1 - this numbers the grid and makes tiles for all static/animated tiles
        while index_i < len(self.index):
            # check if the tile needs to be animated or not
            if self.index[index_i][0] != 1 and self.index[index_i][1] == 1:
                animated = True
            else:
                animated = False

            # determine the last frame of the tiles animation
            end_index[0] = (start_index[0] + self.index[index_i][0] - 1) % self.cols
            end_index[1] = start_index[1] + ((start_index[0] + self.index[index_i][0] - 1) // self.cols)
            # Fill map with integers indicating the tile No
            # Traverse all sprites with indices between the thing, mark with i
            if self.index[index_i][1] == 1:
                for j in range(self.index[index_i][0]):
                    col = (start_index[0] + j) % self.cols
                    row = start_index[1] + ((start_index[0] + j) // self.cols)
                    # CASE NOT NEEDED: Case where animation split by big tile __________________________________________
                    # THIS SHOULD NEVER HAPPEN BUT JUST IN CASE
                    # only do this if not already -1, otherwise while -1, make tile, increment
                    # the original i should be stored though, for finishing the animation
                    self.map[row][col] = self.tile_count
                    # create tile and add it to the tile sheet
                self.tiles.append(Tile(self.img, start_index.copy(), end_index.copy(), animated, 0, 1))
                self.tile_count += 1
            else:
                # If big tile, then fill other rows with -1 and the ones of the same row normally
                for j in range(self.index[index_i][1]):
                    for k in range(self.index[index_i][0]):
                        # Increment value of index being considered
                        col = (start_index[0] + k) % self.cols
                        row = start_index[1] + j + ((start_index[0] + k) // self.cols)
                        if j != 0:
                            self.map[row][col] = -1
                        else:
                            self.map[row][col] = self.tile_count
                            self.tile_count += 1
                            # Create tiles here too probably
                            self.tiles.append(Tile(self.img, [col, row], [col, row], False, 0, 1))

            # move to the next tile on the sheet
            index_i += 1
            start_index = end_index.copy()
            start_index[0] = (start_index[0] + 1) % self.cols
            if start_index[0] == 0:
                start_index[1] += 1
            # Add so that (if) while it's occupied by -1, then make tile and increment current index
            if start_index[1] < len(self.map):
                while self.map[start_index[1]][start_index[0]] == -1:
                    self.map[start_index[1]][start_index[0]] = self.tile_count
                    self.tile_count += 1
                    self.tiles.append(Tile(self.img, start_index.copy(), start_index.copy(), False, 0, 1))
                    start_index[0] = (start_index[0] + 1) % self.cols
                    if start_index[0] == 0:
                        start_index[1] += 1
                        if start_index[1] >= len(self.map):
                            break

        # Continue along spriteSheet to allow incomplete indexes for big tiles
        while start_index[1] < len(self.map):
            if self.map[start_index[1]][start_index[0]] == -1:
                self.map[start_index[1]][start_index[0]] = self.tile_count
                self.tile_count += 1
                self.tiles.append(Tile(self.img, start_index.copy(), start_index.copy(), False, 0, 1))
            start_index[0] = (start_index[0] + 1) % self.cols
            if start_index[0] == 0:
                start_index[1] += 1

        self.printGrid()

        # Pass 2 - this should only loop through all (x,y) to get bigTiles and make new tiles for these
        start_index = [0, 0]
        index_i = 0
        for subIndex in self.index:
            if subIndex[1] != 1:  # If it's a big tile
                selection = []
                for j in range(subIndex[1]):
                    row_select = []
                    for k in range(subIndex[0]):
                        # Increment value of index being considered
                        col = (start_index[0] + k) % self.cols
                        row = start_index[1] + j + ((start_index[0] + k) // self.cols)
                        # Add the tileNo to the selection
                        occupied[row][col] = 1
                        row_select.append(self.map[row][col])
                    selection.append(row_select)
                self.tiles.append(BigTile(selection, self.tile_count))
                self.tile_count += 1

            # Traverse over the thing
            start_index = [(start_index[0] + self.index[index_i][0]) % self.cols,
                           start_index[1] + ((start_index[0] + self.index[index_i][0]) // self.cols)]
            while occupied[start_index[1]][start_index[0]] == 1:  # While it's still occupied, skip it
                start_index = ((start_index[0] + 1) % self.cols,
                               start_index[1] + ((start_index[0] + 1) // self.cols))
            index_i += 1

        # Pass through all tiles and assign animation speed
        for tile_i in range(len(self.tiles)):
            if tile_i < len(self.animation_index):  # If it has an animation speed (a.k.a not big tile)
                self.tiles[tile_i].animation_speed = self.animation_index[tile_i]
                self.tiles[tile_i].type = self.tile_index[tile_i]
            else:
                self.tiles[tile_i].animation_speed = 1
                self.tiles[tile_i].type = -1


    def printGrid(self):
        for row in range(len(self.map)):
            current_row = "["
            for col in range(len(self.map[0])):
                current_row += self.map[row][col].__str__()
                if col != len(self.map[0]) - 1:
                    current_row += " "
                length = self.map[row][col].__str__().__len__()
                for spaces in range(3-length):
                        current_row += " "
            current_row += "]"
            print(current_row)


class Button:
    def __init__(self, pos, size, value, action):
        self.pos = pos
        self.corners = [(pos[0], pos[1]),
                        (pos[0] + size[0], pos[1]),
                        (pos[0] + size[0], pos[1] + size[1]),
                        (pos[0], pos[1] + size[1])]
        self.value = value
        self.action = action

    def contains(self, pos):
        return self.corners[0][0] <= pos[0] <= self.corners[2][0] and \
               self.corners[0][1] <= pos[1] <= self.corners[2][1]

    def draw(self, canvas):
        canvas.draw_polygon(self.corners, 2, "Black", "Lime")
        canvas.draw_text(self.value, (self.pos[0] + 30, self.pos[1] + 25), 20, "Black")


class ToolBox:
    def __init__(self, pos, size, display_size=64):
        self.pos = pos
        self.size = size
        self.corners = [(pos[0], pos[1]),
                        (pos[0] + size[0], pos[1]),
                        (pos[0] + size[0], pos[1] + size[1]),
                        (pos[0], pos[1] + size[1])]
        self.panState = StateBox((pos[0] + 10, pos[1] + 5),
                                 (90, 40),
                                 ("Small Pan", "Large Pan"),
                                 (80, 78))  # The lower this is, the further right you go
        self.fillState = StateBox((pos[0] + 105, pos[1] + 5),
                                  (215, 40),
                                  ("Brush Mode", "Fill Mode: Select Point 1",
                                   "Fill Mode: Select Point 2", "Fill Mode: Choose Tile"),
                                  (100, 200, 200, 190))
        self.bigState = StateBox((pos[0] + 10, pos[1] + 55),
                                 (150, 40),
                                 ("Individual Mode", "Full Tile Mode"),
                                 (130, 120))
        self.selectState = StateBox((pos[0] + 170, pos[1] + 55),
                                    (150, 40),
                                    ("Editing", "Managing Entities"),
                                    (55, 140))
        self.selectState.disabled = True
        self.pickState = StateBox((pos[0] + 330, pos[1] + 5),
                                  (150, 40),
                                  ("Painting", "Picking"),
                                  (60, 55))
        self.entityState = StateBox((pos[0] + 580, pos[1] + 10),
                                    (105, 80),
                                    ("Tile Mode", "Entity Mode"),
                                    (82, 95))
        self.displayBox = SquareTile(pos[0] + 525, pos[1] + 50)
        self.display_size = display_size

    def draw(self, canvas):
        canvas.draw_polygon(self.corners, 2, "Black", "Cyan")
        display = "NOTHING"
        if self.displayBox.tileNo != -1:
            if inputs.tile_sheet.tiles[self.displayBox.tileNo].type == -1:
                display = "BIG_TILE"
            else:
                display = TILE_TYPE[inputs.tile_sheet.tiles[self.displayBox.tileNo].type]
        canvas.draw_text("Type: " + display, (self.pos[0] + 327, self.pos[1] + 80), 15, "Black")
        canvas.draw_text("Brush", (self.pos[0] + 510, self.pos[1] + 30), 25, "Black")
        OFFSET = 16
        canvas.draw_polygon(((self.displayBox.x - OFFSET, self.displayBox.y - OFFSET),
                             (self.displayBox.x - OFFSET + (2*TILE_SIZE), self.displayBox.y - OFFSET),
                             (self.displayBox.x - OFFSET + (2*TILE_SIZE), self.displayBox.y - OFFSET + (2*TILE_SIZE)),
                             (self.displayBox.x - OFFSET, self.displayBox.y - OFFSET + (2*TILE_SIZE))),
                            2, "Black", "White")
        if isinstance(inputs.tile_sheet.tiles[self.displayBox.tileNo], BigTile) and self.displayBox.tileNo != -1:
            big_tile = inputs.tile_sheet.tiles[self.displayBox.tileNo]
            OUT_SIZE = int(self.display_size / max(len(big_tile.tiles), len(big_tile.tiles[0])))
            for y in range(len(big_tile.tiles)):
                for x in range(len(big_tile.tiles[0])):
                    tile = inputs.tile_sheet.tiles[big_tile.tiles[y][x]]
                    src_pos = ((TILE_SIZE / 2) + (tile.current_index[0] * TILE_SIZE),
                               (TILE_SIZE / 2) + (tile.current_index[1] * TILE_SIZE))
                    pos = ((OUT_SIZE / 2) + self.displayBox.x - OFFSET + (OUT_SIZE * x),
                           (OUT_SIZE / 2) + self.displayBox.y - OFFSET + (OUT_SIZE * y))
                    canvas.draw_image(tile.img, src_pos, (TILE_SIZE, TILE_SIZE), pos, (OUT_SIZE, OUT_SIZE))
            canvas.draw_polygon(((self.displayBox.x - OFFSET, self.displayBox.y - OFFSET),
                                 (self.displayBox.x - OFFSET + (2 * TILE_SIZE), self.displayBox.y - OFFSET),
                                 (self.displayBox.x - OFFSET + (2 * TILE_SIZE),
                                 self.displayBox.y - OFFSET + (2 * TILE_SIZE)),
                                 (self.displayBox.x - OFFSET, self.displayBox.y - OFFSET + (2 * TILE_SIZE))),
                                2, "Black")
        else:
            self.displayBox.draw(canvas)
        self.panState.draw(canvas)
        self.fillState.draw(canvas)
        self.bigState.draw(canvas)
        self.selectState.draw(canvas)
        self.entityState.draw(canvas)
        self.pickState.draw(canvas)


class StateBox:
    def __init__(self, pos, size, messages, message_widths=[]):
        self.pos = pos
        self.size = size
        self.msgPos = (pos[0] + 5, pos[1] + (size[1]/2) + 5)
        self.corners = [(pos[0], pos[1]),
                        (pos[0] + size[0], pos[1]),
                        (pos[0] + size[0], pos[1] + size[1]),
                        (pos[0], pos[1] + size[1])]
        self.display = messages[0]
        self.state = 0
        self.messages = messages
        self.message_widths = message_widths
        self.states = len(messages)
        self.disabled = False

    def next(self):
        self.state = (self.state + 1) % self.states
        self.display = self.messages[self.state]

    def set(self, in_state):
        if 0 <= in_state < self.states:
            self.state = in_state
            self.display = self.messages[self.state]

    def contains(self, pos):
        return self.pos[0] <= pos[0] <= self.pos[0]+self.size[0] and \
               self.pos[1] <= pos[1] <= self.pos[1]+self.size[1] and not self.disabled

    def flip(self):
        if self.state == 0:
            self.state = 1
        else:
            self.state = 0
        self.display = self.messages[self.state]

    def draw(self, canvas):
        if self.disabled:
            canvas.draw_polygon(self.corners, 2, "Black", "Grey")
        else:
            canvas.draw_polygon(self.corners, 2, "Black", "Yellow")
        if len(self.message_widths) != 0:
            msg_offset = ((self.size[0] - (2 * 5)) / 2) - (self.message_widths[self.state] / 2) + self.msgPos[0]
            canvas.draw_text(self.display, (msg_offset, self.msgPos[1]), 20, "Black")
        else:
            canvas.draw_text(self.display, self.msgPos, 20, "Black")


class ToolBar:
    def __init__(self, pos, size=(150, 460)):
        self.pos = pos
        self.size = size
        self.corners = [(pos[0], pos[1]),
                        (pos[0] + size[0], pos[1]),
                        (pos[0] + size[0], pos[1] + size[1]),
                        (pos[0], pos[1] + size[1])]
        self.displayBox = SquareTile(pos[0] + 100, pos[1] + 10, False, 0)
        self.actionButton = StateBox((pos[0]+35, pos[1]+415), (80, 40),
                                     ("Selecting", "Adding", "Deleting"),
                                     (70, 60, 65))
        self.actionButton.disabled = True
        self.extraButton = StateBox((pos[0]+35, pos[1]+155), (80, 40),
                                    ("Viewing", "Setting"),
                                    (66, 52))
        self.extra_value = ""
        self.entity = None
        self.list = ListBox((pos[0]+5, pos[1]+115))

    def setEntity(self, entity):
        self.entity = entity
        self.list.contacts = []
        self.list.frameStart = 0
        if entity is not None:
            self.displayBox.tileNo = entity.type
            self.actionButton.disabled = not self.entity.trigger
            for contact in entity.contacts:
                self.list.addContact(contact)
            if self.entity.extra is not None:
                extra = str(self.entity.extra)
                if self.entity.type == 11:
                    self.extra_value = "Point"
                elif self.entity.type == 12:
                    self.extra_value = "Range"
            else:
                self.extra_value = ""
        else:
            self.actionButton.disabled = True
            self.extraButton.set(0)
            self.extra_value = ""
            self.displayBox.tileNo = 0

    def addTimer(self, time):
        if self.entity is None:
            return False
        if self.entity.timer is not None and time > 0:
            self.entity.timer = time
            return True
        else:
            return False

    def draw(self, canvas):
        canvas.draw_polygon(self.corners, 2, "Black", "Cyan")
        canvas.draw_text("Selected:", (self.pos[0] + 20, self.pos[1] + 30), 20, "Black")
        if self.entity is not None:
            trigger = str(self.entity.trigger)
            position = str(self.entity.pos)
            if self.entity.timer is not None:
                timer = str(self.entity.timer)
                canvas.draw_text("Timer: " + timer, (self.pos[0] + 20, self.pos[1] + 110), 20, "Black")
            canvas.draw_text("Trigger: " + trigger, (self.pos[0] + 20, self.pos[1] + 60), 20, "Black")
            canvas.draw_text("Position: " + position, (self.pos[0] + 20, self.pos[1] + 85), 20, "Black")
        self.displayBox.draw(canvas)
        if self.entity is not None:
            if self.entity.trigger:
                self.list.draw(canvas)
            elif self.extra_value != "":
                extra = str(self.entity.extra)
                canvas.draw_text(self.extra_value + ": " + extra, (self.pos[0] + 20, self.pos[1] + 135), 18, "Black")
                self.extraButton.draw(canvas)
        self.actionButton.draw(canvas)


class ListBox:
    def __init__(self, pos, size=(140, 280)):
        self.pos = pos
        self.size = size
        self.corners = [(pos[0], pos[1]),
                        (pos[0] + size[0], pos[1]),
                        (pos[0] + size[0], pos[1] + size[1]),
                        (pos[0], pos[1] + size[1])]
        self.contacts = []
        self.frameStart = 0
        self.frame = 5

    def addContact(self, contact_entity, new=False):
        if toolbar.entity is None:
            return
        if not toolbar.entity.trigger:
            return
        for contact in self.contacts:
            if contact.entity.__eq__(contact_entity):
                return
        if toolbar.entity.__eq__(contact_entity):
            return
        if toolbar.entity.type == 4 and len(toolbar.entity.contacts) == 1 and new:  # If it's a button and has one contact
            return
        if not contact_entity.target:
            return
        if new:
            toolbar.entity.addContact(contact_entity)
        visible = False
        if self.frameStart <= len(self.contacts) < self.frameStart + self.frame:
            visible = True
        self.contacts.append(
            Contact([self.pos[0] + 5, self.pos[1] + (len(self.contacts) * 55) + 5], contact_entity, visible))

    def remove(self, contact_entity):
        # Shift all items up if found
        index = -1
        for i in range(len(self.contacts)):
            if self.contacts[i].entity.__eq__(contact_entity):
                index = i
                break
        if index == -1:
            return
        else:
            toolbar.entity.contacts.remove(contact_entity)
            # Only ever going to happen in between so checking not required
            for i in range(len(self.contacts)):
                if i > index:
                    self.contacts[i].shift(-55)
            if self.frameStart + self.frame < len(self.contacts):  # If there is a next one, set it to visible
                self.contacts[self.frameStart + self.frame].visible = True
            elif self.frameStart == 0:  # If can't scroll up since at the start, do nothing
                pass
            else:  # Otherwise, if there is no next, scroll up
                self.frameStart -= 1
                self.contacts[self.frameStart].visible = True
                for contact in self.contacts:
                    contact.shift(55)
            self.contacts.remove(self.contacts[index])

    def click(self, pos):
        if self.pos[0] <= pos[0] <= self.pos[0] + self.size[0] and \
           self.pos[1] <= pos[1] <= self.pos[1] + 10:
            self.scroll(-1)
        elif self.pos[0] <= pos[0] <= self.pos[0] + self.size[0] and \
             self.pos[1] + self.size[1] - 10 <= pos[1] <= self.pos[1] + self.size[1]:
            self.scroll(1)

    def scroll(self, mag):
        if mag == 1 and self.frameStart + self.frame < len(self.contacts):
            self.contacts[self.frameStart].visible = False
            self.contacts[self.frameStart+self.frame].visible = True
        elif mag == -1 and self.frameStart != 0:
            self.contacts[self.frameStart-1].visible = True
            self.contacts[self.frameStart+self.frame-1].visible = False
        else:
            return
        self.frameStart += mag
        for contact in self.contacts:
            contact.shift(-55*mag)

    def draw(self, canvas):
        canvas.draw_polygon(self.corners, 2, "Black", "Grey")
        canvas.draw_polygon([(self.pos[0], self.pos[1]),
                             (self.pos[0] + self.size[0], self.pos[1]),
                             (self.pos[0] + self.size[0], self.pos[1] + 10),
                             (self.pos[0], self.pos[1] + 10)], 2, "Black", "Yellow")
        canvas.draw_polygon([(self.pos[0], self.pos[1] + self.size[1]),
                             (self.pos[0] + self.size[0], self.pos[1] + self.size[1]),
                             (self.pos[0] + self.size[0], self.pos[1] + self.size[1] - 10),
                             (self.pos[0], self.pos[1] + self.size[1] - 10)], 2, "Black", "Yellow")
        for i in range(self.frame):
            if i+self.frameStart < len(self.contacts) and self.contacts[i+self.frameStart].visible:
                self.contacts[i+self.frameStart].draw(canvas)


class Contact:
    def __init__(self, pos, entity, visible, size=(130, 50)):
        self.pos = pos
        self.size = size
        self.corners = [(self.pos[0], self.pos[1]),
                        (self.pos[0] + self.size[0], self.pos[1]),
                        (self.pos[0] + self.size[0], self.pos[1] + self.size[1]),
                        (self.pos[0], self.pos[1] + self.size[1])]
        self.visible = visible
        self.entity = entity
        self.displayBox = SquareTile(pos[0] + 10, pos[1] + 10, False, entity.type)
        self.clickCount = 0

    def draw(self, canvas):
        back_colour = "White"
        if self.clickCount != 0:
            back_colour = "Yellow"
        canvas.draw_polygon(self.corners, 2, "Black", back_colour)
        self.displayBox.draw(canvas)
        canvas.draw_text("Pos: " + str(self.entity.pos), (self.pos[0] + 50, self.pos[1] + 30), 15, "Black")

    def shift(self, shift):
        self.pos[1] += shift
        self.corners = [(self.pos[0], self.pos[1]),
                        (self.pos[0] + self.size[0], self.pos[1]),
                        (self.pos[0] + self.size[0], self.pos[1] + self.size[1]),
                        (self.pos[0], self.pos[1] + self.size[1])]
        self.displayBox.shiftY(shift)

    def contains(self, pos):
        if toolbar.entity is None:
            return False
        return self.visible and toolbar.entity.trigger and self.pos[0] <= pos[0] <= self.pos[0]+self.size[0] \
            and self.pos[1] <= pos[1] <= self.pos[1]+self.size[1]

    def click(self, pos):
        if self.contains(pos):
            self.clickCount += 1
            if self.clickCount == 2:
                if toolbar.actionButton.state != 2:
                    toolbar.setEntity(self.entity)
                    toolbar.actionButton.set(0)
                    toolbar.actionButton.disabled = not toolbar.entity.trigger
                else:  # Deleting
                    toolbar.list.remove(self.entity)
        else:
            self.clickCount = 0
        return self.contains(pos)


class Input:
    tile_sheet = 0
    tile_path = ""
    bigTiles = []
    entities = []

    def __init__(self):
        self.brush = -1
        self.otherBrush = -1
        self.selectStart = [0, 0]
        self.selectEnd = [0, 0]

    def click(self, pos):
        if level_tile_grid.contains(pos):
            if tools.pickState.state != 1:
                if tools.fillState.state == 1:  # Start and end selections
                    self.selectStart = level_tile_grid.get_selected(pos, False)
                    tools.fillState.next()
                elif tools.fillState.state == 2:
                    self.selectEnd = level_tile_grid.get_selected(pos, False)
                    tools.fillState.next()
                self.set_colour(pos)  # Paint cells after
            else:  # If picking
                self.brush = level_tile_grid.get_selected(pos).tileNo
                tools.pickState.set(0)
                tools.displayBox.paint(self.brush)
                print(self.brush)
                if tools.fillState.state == 3:
                    self.fill()
        elif level_entity_grid.contains(pos):
            if tools.selectState.state == 1:  # If we are selecting entities
                if toolbar.entity is not None and toolbar.extraButton.state == 1:  # If we are assigning extra values
                    click_pos = level_entity_grid.get_selected(pos, False)
                    click_xy = [click_pos[1], click_pos[0]]
                    if (click_xy[1] == toolbar.entity.pos[1]) ^ (click_xy[0] == toolbar.entity.pos[0]):  # If in line
                        if toolbar.entity.type == 11:  # If it's a scientist point
                            toolbar.entity.extra = click_xy
                        elif toolbar.entity.type == 12:  # If it's a missile launcher range
                            toolbar.entity.extra = [int((Vector(click_xy) - Vector(toolbar.entity.pos)).length())]
                else:
                    if toolbar.actionButton.state != 2:  # If we aren't deleting contacts
                        # Get the FakeEntity chosen, if any
                        entity_pos = level_entity_grid.get_selected(pos, False)
                        if level_entity_grid.tiles[entity_pos[0]][entity_pos[1]].tileNo != -1:  # If entity was clicked
                            entity = 0
                            for test_entity in self.entities:
                                if (test_entity.pos == [entity_pos[1], entity_pos[0]] and test_entity.type != 1) or \
                                        (test_entity.pos == [entity_pos[0], entity_pos[1]] and test_entity.type == 1):  # Find it by position
                                    entity = test_entity
                                    break
                            if toolbar.actionButton.state == 0:
                                toolbar.setEntity(entity)
                            else:
                                toolbar.list.addContact(entity, True)
                        else:
                            if toolbar.actionButton.state == 0:
                                toolbar.setEntity(None)
            else:
                self.set_colour(pos)  # No filling required
        elif entity_grid.contains(pos):
            if tools.selectState.state == 0:
                selected_tile = entity_grid.get_selected(pos, False)
                self.brush = entity_grid.tiles[selected_tile[0]][selected_tile[1]].tileNo
                tools.displayBox.paint(self.brush)
        elif tile_grid.contains(pos):
            selected_tile = tile_grid.get_selected(pos, False)
            if tools.bigState.state == 0:
                self.brush = tile_grid.map[selected_tile[0]][selected_tile[1]]
            else:
                # check if is contained in all bigTiles
                updated = False
                for bigTile in self.bigTiles:
                    if bigTile.contains(tile_grid.map[selected_tile[0]][selected_tile[1]]):
                        self.brush = bigTile.tileNo
                        updated = True
                if not updated:
                    self.brush = tile_grid.map[selected_tile[0]][selected_tile[1]]
            tools.displayBox.paint(self.brush)
            print(self.brush)
            self.fill()
        elif tools.bigState.contains(pos):
            tools.bigState.flip()
        elif tools.panState.contains(pos):
            tools.panState.flip()
        elif tools.fillState.contains(pos):
            if tools.fillState.state != 0:
                tools.fillState.set(0)
            else:
                tools.fillState.set(1)
        elif tools.entityState.contains(pos):
            self.editSwap()
        elif tools.selectState.contains(pos):
            if toolbar.entity is not None:
                if level_entity_grid.tiles[toolbar.entity.pos[1]][toolbar.entity.pos[0]].tileNo != \
                        toolbar.entity.type:  # If overwritten
                    toolbar.entity = None
                    toolbar.displayBox.tileNo = 0
            tools.selectState.flip()
        elif toolbar.actionButton.contains(pos):
            toolbar.actionButton.next()
        elif toolbar.extraButton.contains(pos):
            if toolbar.entity is not None:
                if toolbar.entity.extra is not None:
                    toolbar.extraButton.flip()
        elif play_button.contains(pos):
            play_button.action()
        elif menu_button.contains(pos):
            menu_button.action()
        elif tools.pickState.contains(pos):
            tools.pickState.flip()

        contacted = False
        for contact in toolbar.list.contacts:
            if not contacted:
                contacted = contact.click(pos)
            else:
                contact.click(pos)
        if not contacted:
            toolbar.list.click(pos)

    def set_colour(self, pos):
        if tools.pickState.state == 1:
            return
        if tools.entityState.state == 0:
            if self.brush != -1 and tools.fillState.state == 0 and level_tile_grid.contains(pos):
                if isinstance(self.tile_sheet.tiles[self.brush], BigTile):
                    big_in_use = self.tile_sheet.tiles[self.brush]
                    selected_index = level_tile_grid.get_selected(pos, False)
                    for y in range(len(big_in_use.tiles)):
                        for x in range(len(big_in_use.tiles[0])):
                            if x+selected_index[1] < level_tile_grid.cols and y+selected_index[0] < level_tile_grid.rows:
                                level_tile_grid.tiles[y + selected_index[0]][x + selected_index[1]].paint(big_in_use.tiles[y][x])
                else:
                    level_tile_grid.get_selected(pos).paint(self.brush)
        else:
            selected = level_tile_grid.get_selected(pos, False)  # Returns [y,x]
            # Ignore if occupied by player or the brush is invalid or selecting or if overwriting by same entity
            if level_entity_grid.tiles[selected[0]][selected[1]].tileNo != 1 and self.brush != -1 \
                    and tools.selectState.state == 0 and level_entity_grid.contains(pos) \
                    and level_entity_grid.get_selected(pos).tileNo != self.brush:
                is_player = (self.brush == 1)  # If player
                if level_entity_grid.tiles[selected[0]][selected[1]].tileNo != -1:  # If not empty
                    # Loop through entities to check which one is in there
                    entity_delete = 0
                    for entity in self.entities:
                        if entity.pos == [selected[1], selected[0]]:  # If position matches select it
                            entity_delete = entity
                    # Remove this entity from all contacts
                    entity_delete.remove()
                if is_player:
                    player = self.entities[0]
                    level_entity_grid.tiles[player.pos[0]][player.pos[1]].tileNo = -1  # Remove player from old pos
                    player.pos = [selected[0], selected[1]]  # Change player position
                elif self.brush != 0:
                    self.entities.append(FakeEntity([selected[1], selected[0]], self.brush))  # Add entity to list
                if self.brush == 0:
                    level_entity_grid.tiles[selected[0]][selected[1]].paint(-1)  # Remove entity from grid
                else:
                    level_entity_grid.tiles[selected[0]][selected[1]].paint(self.brush)  # Add entity to grid

    def editSwap(self):
        tools.entityState.flip()
        # Toggles which grids can be interacted with
        level_tile_grid.inactive = not level_tile_grid.inactive
        level_entity_grid.inactive = not level_entity_grid.inactive
        tile_grid.inactive = not tile_grid.inactive
        entity_grid.inactive = not entity_grid.inactive
        # Toggles which grids can be seen
        level_entity_grid.hidden = not level_entity_grid.hidden
        tile_grid.hidden = not tile_grid.hidden
        entity_grid.hidden = not entity_grid.hidden
        # Swap brushes
        self.brush, self.otherBrush = self.otherBrush, self.brush
        # Reset fill selection state
        tools.fillState.set(0)
        # Reset selected box
        tools.displayBox.tileNo = self.brush
        tools.displayBox.tile = not tools.displayBox.tile
        # Draws disabled buttons correctly
        tools.fillState.disabled = not tools.fillState.disabled
        tools.bigState.disabled = not tools.bigState.disabled
        tools.selectState.disabled = not tools.selectState.disabled
        tools.panState.disabled = not tools.panState.disabled
        tools.pickState.disabled = not tools.pickState.disabled

    def fill(self):
        if tools.fillState.state == 3:  # If filling
            if isinstance(self.tile_sheet.tiles[self.brush], BigTile):
                big_in_use = self.tile_sheet.tiles[self.brush]
                selected = level_tile_grid.in_selection(self.selectStart, self.selectEnd, True)
                for dy in range((selected[1][0] - selected[0][0] + 1) // len(big_in_use.tiles)):
                    sy = dy * len(big_in_use.tiles) + selected[0][0]
                    for dx in range((selected[1][1] - selected[0][1] + 1) // len(big_in_use.tiles[0])):
                        selected_index = [sy, dx * len(big_in_use.tiles[0]) + selected[0][1]]
                        for y in range(len(big_in_use.tiles)):  # Draws the tile
                            for x in range(len(big_in_use.tiles[0])):
                                if x + selected_index[1] < level_tile_grid.cols and y + selected_index[0] \
                                        < level_tile_grid.rows:
                                    level_tile_grid.tiles[y + selected_index[0]][x + selected_index[1]].paint(
                                        big_in_use.tiles[y][x])
            else:
                selected = level_tile_grid.in_selection(self.selectStart, self.selectEnd)
                for tile in selected:
                    tile.paint(self.brush)
            tools.fillState.next()

def init_tile_grid():
    global tile_grid
    tile_grid = Grid(40, 26, 50, 50, (8, 13), -1, True, False, False)
    # Identify and store all big_tiles in separate array
    big_tiles = []
    for tile in inputs.tile_sheet.tiles:
        if isinstance(tile, BigTile):
            big_tiles.append(tile)
    inputs.bigTiles = big_tiles

    # In copy of index, remove all references in big_tiles except topLeft
    to_remove = []
    for bigTile in big_tiles:
        for y in range(len(bigTile.tiles)):
            for x in range(len(bigTile.tiles[0])):
                to_remove.append(inputs.tile_sheet.tiles[bigTile.tiles[y][x]])
    leftovers = inputs.tile_sheet.tiles.copy()
    for tile in to_remove:
        if tile in leftovers:
            leftovers.remove(tile)

    # Render onto tileGrid
    current_index = [0, 0]
    cols = tile_grid.cols
    rows = tile_grid.rows

    buffer = []
    grid = []
    for y in range(rows):
        current_row = []
        for x in range(cols):
            current_row.append(-1)
        grid.append(current_row)

    for tile in leftovers:
        # If not occupied already
        if grid[current_index[1]][current_index[0]] == -1:
            # Try to draw the big tile immediately if possible, otherwise add to the buffer
            if isinstance(tile, BigTile):
                if buffer_check(current_index, tile, grid, 1):
                    # If enough space, draw
                    for y in range(len(tile.tiles)):
                        for x in range(len(tile.tiles[0])):
                            grid[current_index[1]+y][current_index[0]+x] = tile.tiles[y][x]
                            tile_grid.tiles[current_index[1] + y][current_index[0] + x].tileNo = tile.tiles[y][x]
                    # Add x length to current index
                    current_index = [(current_index[0] + len(tile.tiles[0])) % cols,
                                     current_index[1] + ((current_index[0] + len(tile.tiles[0])) // cols)]
                else:
                    buffer.append(tile)
            else:
                # If buffer isn't empty and is empty-able then do it
                if len(buffer) != 0:
                    for buffer_tile in buffer:
                        if buffer_check(current_index, tile, grid):
                            # If enough space, draw
                            for y in range(len(buffer_tile.tiles)):
                                for x in range(len(buffer_tile.tiles[0])):
                                    grid[current_index[1] + y][current_index[0] + x] = buffer_tile.tiles[y][x]
                                    tile_grid.tiles[current_index[1] + y][current_index[0] + x].tileNo = \
                                        buffer_tile.tiles[y][x]
                            # Add x length to current index
                            current_index = [(current_index[0] + len(buffer_tile.tiles[0])) % cols,
                                             current_index[1] + ((current_index[0] + len(buffer_tile.tiles[0])) // cols)]
                            buffer.remove(buffer_tile)
                # Add original index into the grid
                tile_no = inputs.tile_sheet.tiles.index(tile)
                grid[current_index[1]][current_index[0]] = tile_no
                tile_grid.tiles[current_index[1]][current_index[0]].tileNo = tile_no
                current_index = [(current_index[0] + 1) % cols,
                                 current_index[1] + ((current_index[0] + 1) // cols)]
    while len(buffer) != 0 and current_index[1] != rows:
        added = False
        for buffer_tile in buffer:
            if buffer_check(current_index, buffer_tile, grid):
                # If enough space, draw
                added = True
                for y in range(len(buffer_tile.tiles)):
                    for x in range(len(buffer_tile.tiles[0])):
                        grid[current_index[1] + y][current_index[0] + x] = buffer_tile.tiles[y][x]
                        tile_grid.tiles[current_index[1] + y][current_index[0] + x].tileNo = \
                            buffer_tile.tiles[y][x]
                # Add x length to current index
                current_index = [(current_index[0] + len(buffer_tile.tiles[0])) % cols,
                                 current_index[1] + ((current_index[0] + len(buffer_tile.tiles[0])) // cols)]
                buffer.remove(buffer_tile)

        if not added:
            current_index = [(current_index[0] + 1) % cols,
                             current_index[1] + ((current_index[0] + 1) // cols)]
    if len(buffer) != 0:
        print(len(buffer).__str__() + " tiles not rendered due to space")
    else:
        print("All tiles rendered successfully")
    print("______________________________Selected Brush Tile No.______________________________")
    tile_grid.map = grid


def buffer_check(current_index, tile, grid, offset=0):
    if current_index[0] + len(tile.tiles[0]) + offset > tile_grid.cols:
        return False
    elif current_index[1] + len(tile.tiles) + offset > tile_grid.rows:
        return False
    else:
        for i in range(len(tile.tiles[0])):
            if grid[current_index[1]][current_index[0] + i] != -1:
                return False
    return True

# Attempt at a buffer_draw failed due to not being able to modify grid enough in the way it is passed


def init_entity_grid():
    global entity_grid
    entity_grid = Grid(8, 3, 50, 50, (8, 3), -1, False, True, True)
    current_index = [0, 0]

    for entityNo in range(len(ENTITY_SRC_POS)):
        entity_grid.tiles[current_index[1]][current_index[0]].tileNo = entityNo
        current_index = [(current_index[0] + 1) % entity_grid.cols,
                         current_index[1] + ((current_index[0] + 1) // entity_grid.cols)]
        if current_index[1] >= entity_grid.rows:
            print("Couldn't fill all entities")
            return


def i_save():
    global game
    name = game._game.editor_level
    if name[0] == '_':
        name = name[1:]
    save(name)


def save(name):
    global game
    if len(name) == 0:
        return
    if name[0] == "_":  # If it starts with an underscore, it's a in-built level, can't be replaced
        return

    game._game.editor_level = name
    file = open("../assets/levels/" + name + ".txt", "wt+")
    expFile.set_text("")
    # write tilesheet path
    buffer = inputs.tile_path + "\n"
    file.write(buffer)

    # save tilemap
    file.write("MAP_START\n")
    for y in range(len(level_tile_grid.tiles)):
        buffer = []
        for tile in level_tile_grid.tiles[y]:
            buffer.append(tile.tileNo)
        file.write(buffer.__str__().strip("[]").replace(" ", "") + "\n")
    file.write("MAP_END\n")

    # save entities
    file.write("ENTITIES_START\n")
    for entity in inputs.entities:
        buffer = entity.save_data() + "\n"
        file.write(buffer)
    file.write("ENTITIES_END\n")

    # save contacts
    file.write("CONTACTS_START\n")
    for entity in inputs.entities:
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


def list_csv_big(buffer):
    data = []
    unit = []
    val = ""
    for c in buffer:
        if c == ",":
            unit.append(int(val))
            val = ""
            data.append(unit)
            unit = []
        elif c == ".":
            unit.append(int(val))
            val = ""
        else:
            val += c
    unit.append(int(val))
    data.append(unit)
    return data


def load_level(path):
    global level_tile_grid, level_entity_grid, level_loaded, game

    try:
        file = open('../assets/levels/' + path + '.txt', "rt")
    except OSError as e:
        print("File not Found")
        return

    level_loaded = False
    # change to tile view
    toolbar.setEntity(None)
    if tools.entityState.state == 1:
        inputs.editSwap()

    game._game.editor_level = path
    # read source tilesheet path
    load_tileSheet(file.readline().strip("\n"))

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
    level_tile_grid = Grid(len(map[0]), len(map), 350, 50, (10, 10), 0, True, False, False, map)
    level_entity_grid = Grid(len(map[0]), len(map), 350, 50, (10, 10), -1, False, True, True)

    inputs.entities = []

    # retrieve entity data and create entities
    inputs.entities.append(FakeEntity([0, 0], 1))
    level_entity_grid.tiles[0][0].tileNo = 1
    for line in file:
        buffer = line.strip("\n")
        if buffer == "ENTITIES_START":
            continue
        elif buffer == "ENTITIES_END":
            break

        data = list_csv(buffer)
        if data[0] > 1:  # If not an invalid or player entity
            if level_entity_grid.tiles[data[2]][data[1]].tileNo == -1:  # If empty
                timer = -1
                extra = []
                if ENTITY_OTHER[data[0]] is not None:  # If it's supposed to have extra data, assign it
                    no = 1
                    if data[0] == 11:  # If scientist, use 2 indexes
                        no = 2
                    elif data[0] == 12:  # If missile launcher, use 1 index
                        pass
                    for i in range(no):
                        extra.append(data[3+i])
                if ENTITY_TIMER[data[0]] != -1:  # If it's supposed to have a timer, assign it as the last one
                    if len(data) > 3:  # Only if more than the position is defined      ||FUSE WILL ALWAYS BE READ||
                        timer = data[-1]
                inputs.entities.append(FakeEntity([data[1], data[2]], data[0], timer, extra))  # Add entity to list
                level_entity_grid.tiles[data[2]][data[1]].tileNo = data[0]  # Add entity to entity grid
        elif data[0] == 1:
            player = inputs.entities[0]
            level_entity_grid.tiles[player.pos[1]][player.pos[0]].tileNo = -1  # Remove player from old pos
            player.pos = [data[2], data[1]]  # Change player position
            level_entity_grid.tiles[data[2]][data[1]].tileNo = data[0]  # Move player in entity grid

    for line in file:
        buffer = line.strip("\n")
        if buffer == "CONTACTS_START":
            continue
        elif buffer == "CONTACTS_END":
            break
        data = list_csv(buffer)
        inputs.entities[data[0]-1].contacts.append(inputs.entities[data[1]-1])

    init_entity_grid()
    level_loaded = True


def load_tileSheet(path):
    global tile_grid
    # create an empty list to store the three indexes
    index = []

    # open the tilesheet file
    file = open(path, "rt")

    # read source image path
    img_path = file.readline().strip("\n")

    # read animation frame, types and animation speed index
    # data and store them as individual lists
    print("______________________________ Indexes in Tile Sheet ______________________________")
    for i in range(3):
        buffer = file.readline().strip("\n")
        index.append(list_csv(buffer))
        print(index[-1])
    buffer = file.readline().strip("\n")
    index.append(list_csv_big(buffer))
    print(index[-1])
    print("______________________________Sprite Sheet Being Read______________________________")

    # create new tilesheet
    inputs.tile_sheet = LevelTileSheet(img_path, index[3], index[1], index[2])
    inputs.tile_path = path

    # close the level file
    file.close()

    init_tile_grid()


# Default starting screen
tools = ToolBox((50, CANVAS_DIMS[1] - 100), (700, 100))
toolbar = ToolBar((CANVAS_DIMS[0] - 200, 20))
level_tile_grid = 0
level_entity_grid = 0
tile_grid = 0
entity_grid = 0
inputs = Input()
load_level(game._game.editor_level)


def play():
    game._game.launch_sandbox()
    game._game.close = False
    frame.stop()
play_button = Button((CANVAS_DIMS[0] - 125, CANVAS_DIMS[1] - 100), (100, 40), "Play", play)


def menu():
    game._game.close = False
    frame.stop()
menu_button = Button((CANVAS_DIMS[0] - 125, CANVAS_DIMS[1] - 50), (100, 40), "Menu", menu)


def click(pos):
    inputs.click(pos)


def drag(pos):
    inputs.set_colour(pos)


def draw(canvas):
    global _game
    if level_loaded:
        for i in range(len(inputs.tile_sheet.tiles)):
            # resets the update flags on all tiles before drawing them
            inputs.tile_sheet.tiles[i].updated = False
        level_tile_grid.draw(canvas)
        level_entity_grid.draw(canvas)
        tile_grid.draw(canvas)
        entity_grid.draw(canvas)
        tools.draw(canvas)
        play_button.draw(canvas)
        menu_button.draw(canvas)
        canvas.draw_text("WASD to scroll", (50, 40), 15, "White")
        canvas.draw_text("Arrow Keys to scroll", (350, 40), 15, "White")
        if tools.entityState.state == 1 and tools.selectState.state == 1:
            toolbar.draw(canvas)
        game._game.clock.tick()
    else:
        game._game.clock.reset()

def load(name):
    load_level(name)
    impFile.set_text("")

def add_timer(time_str):
    if toolbar.addTimer(int(time_str)):
        addTimer.set_text("")


def resize(input_str):
    input_dims = list_csv(input_str.strip("()"))
    # If entities will be cut, remove them from the list, except for player where it is repositioned to origin
    to_remove = []
    for i in range(len(inputs.entities)):
        if inputs.entities[i].pos[0] >= input_dims[0] or inputs.entities[i].pos[1] >= input_dims[1]:
            if i == 0:
                level_entity_grid.tiles[0][0].tileNo = 1
                inputs.entities[0].pos = [0, 0]
            else:
                to_remove.append(inputs.entities[i])
    for deleted_entity in to_remove:
        deleted_entity.remove()
    level_tile_grid.resize(input_dims)
    level_entity_grid.resize(input_dims)
    changeDims.set_text("")


def key_down(key):
    # Perhaps have a select case
    if key == simplegui.KEY_MAP['up']:  # To control level camera
        level_tile_grid.move_frame(0, -1)
        level_entity_grid.move_frame(0, -1)
    elif key == simplegui.KEY_MAP['left']:
        level_tile_grid.move_frame(-1, 0)
        level_entity_grid.move_frame(-1, 0)
    elif key == simplegui.KEY_MAP['down']:
        level_tile_grid.move_frame(0, 1)
        level_entity_grid.move_frame(0, 1)
    elif key == simplegui.KEY_MAP['right']:
        level_tile_grid.move_frame(1, 0)
        level_entity_grid.move_frame(1, 0)
    elif key == simplegui.KEY_MAP['w']:  # To control palette camera
        if tools.panState.state == 1:
            tile_grid.move_frame(0, -(tile_grid.frame[1]))
        else:
            tile_grid.move_frame(0, -1)
    elif key == simplegui.KEY_MAP['a']:
        if tools.panState.state == 1:
            tile_grid.move_frame(-(tile_grid.frame[0]), 0)
        else:
            tile_grid.move_frame(-1, 0)
    elif key == simplegui.KEY_MAP['s']:
        if tools.panState.state == 1:
            tile_grid.move_frame(0, (tile_grid.frame[1]))
        else:
            tile_grid.move_frame(0, 1)
    elif key == simplegui.KEY_MAP['d']:
        if tools.panState.state == 1:
            tile_grid.move_frame(tile_grid.frame[0], 0)
        else:
            tile_grid.move_frame(1, 0)
    elif key == simplegui.KEY_MAP['i']:  # Hotkey for immediate save
        i_save()
    elif key == simplegui.KEY_MAP['p']:  # Hotkey to play level
        play()


frame = simplegui.create_frame("LevelEditor", CANVAS_DIMS[0], CANVAS_DIMS[1])

frame.set_mouseclick_handler(click)
frame.set_keydown_handler(key_down)
frame.set_mousedrag_handler(drag)

impFile = frame.add_input("Load: Level Name", load, 100)
expFile = frame.add_input("Save: Level Name", save, 100)

changeDims = frame.add_input("Resize: (Width, Height)", resize, 100)
addTimer = frame.add_input("Add Timer: Time (s)", add_timer, 100)

frame.add_label("Hotkeys:")
frame.add_label("'I' to save into current file")
frame.add_label("'p' to play current level")

frame.set_draw_handler(draw)
frame.start()
