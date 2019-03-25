try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from enum import IntEnum
import game

TILESIZE = 32 # constant storing the size of all tiles in the game
HALFSIZE = 16 # constant storing the half size of all tiles in the game
TILE_DIMS = (TILESIZE, TILESIZE) # tuple simply containing two instances of the tilesize

FRAMEWIDTH, FRAMEHEIGHT = 640, 480 # the canvas dimensions
# the maximum number of columns of tiles displayable on screen with the current canvas width
MAX_TILES_X = FRAMEWIDTH / TILESIZE
# the maximum number of rows of tiles displayable on screen with the current canvas height
MAX_TILES_Y = FRAMEHEIGHT / TILESIZE

# the tile types are indicators of the behaviour of the various tiles in the gamed
class TileType(IntEnum):

    EMPTY          = 0 # any regular tile which can be stepped on
    SOLID          = 1 # any regular tile which acts as a wall
    ICY            = 2 # tiles which make the player slide
    LEFT_FENCE     = 3 # tiles which can be jumped over from the right
    RIGHT_FENCE    = 4 # tile which can be jumped over from the left
    CONVEYOR_UP    = 5 # tile which forces the player to move up
    CONVEYOR_LEFT  = 6 # tile which forces the player to move left
    CONVEYOR_DOWN  = 7 # tile which foces the player to move down
    CONVEYOR_RIGHT = 8 # tile which forces the player to move right
    SPIKES         = 9 # tile which kills the player when stepped on
    OPEN_PIT       = 10 # tile which kills the player when stepped on but can be blocked
                        # using crates
    CLOSED_PIT     = 11 # the "open tile" after it has been blocked by a crate. no longer
                        # kills the player when stepped on and instead acts as a bridge
    GLUE           = 12 # tile which kills the player when stepped on. Creates also get stuck
                        # on these tiles when pushed on to them
    UP_FENCE       = 13 # tile which can be jumped over from the top
    FIRE           = 14 # tile which kills the player when stepped on
    FAN            = 15 # tile which kills the player when stepped on
    WATER          = 16 # tile which kills the player when stepped on
    LASER          = 17 # tile which kills the player when stepped on
    GHOST          = 18 # tile which kills the player when stepped on
    GOAL           = 19 # tile which kills the player when stepped

# the tile stores data on how each tile should be drawn and how their type, which is
# an indicator of how other objects in the game should behave when they come into contact with
# the tile
class Tile:

    def __init__(self, img, start_index, end_index, animated, type, speed):

        # reference of the tilesheet from the containing tilesheet class
        self.img = img
        self.cols = self.img.get_width() // TILESIZE

        self.type = type

        self.start_index = start_index
        self.end_index = end_index
        self.current_index = self.start_index.copy()

        self.animated = animated # a flag to keep track of whether or not a tile is meant to be animated
        self.animation_speed = speed # stores the animation speed of an tile
        # keeps track of if a certain tile's animation has already been cycled forward a frame.
        # this is to stop other tiles of the same type cylcing the animation forward on the same frame
        self.updated = False

    # method which sets the animation speed of a tile
    def set_animation_speed(self, speed):
        self.animation_speed = speed

    # handles the drawing of each tile
    def draw(self, canvas, x, y):
        pos = (x, y) # stores the tiles position index as a tuple
        # determines the actual position on the canvas where the tile should be drawn
        src_pos = (HALFSIZE + (self.current_index[0] * TILESIZE), HALFSIZE +  (self.current_index[1] * TILESIZE))
        # draws the tile
        canvas.draw_image(self.img, src_pos, TILE_DIMS, pos, TILE_DIMS)

        # tiles are not animated if the game is paused
        if game._game.state != game.GameState.PAUSE:
            # checks if this tile animation has already been updated
            if not self.updated:
                if self.animated:
                    if game._game.clock.transition(self.animation_speed):
                        self.nextFrame()
                        # sets the updated flag to true so avoid extra updates
                        self.updated = True

    # determines the next animation frame of any animated tiles
    def nextFrame(self):
        if self.current_index == self.end_index:
            self.current_index = self.start_index.copy()
        else:
            self.current_index[0] = (self.current_index[0] + 1) % self.cols
            if self.current_index[0] == 0: self.current_index[1] += 1


# the tilesheet class takes an external tilesheet image and several lists of indexes to build
# the set of tiles to be used for a level
class Tilesheet:

    def __init__(self, img_path, index, types, speeds):

        # source image for tile sheet
        self.img_path = img_path
        self.img = simplegui._load_local_image(self.img_path)

        # automatically assumes the number of tiles in the tilesheet
        # based on the sheets dimensions and the tilesize
        self.cols = self.img.get_width() // TILESIZE

        self.index = index # a list or values detailing how many animation frames each tile has
        self.types = types # a list of values detailing what behaviour each tile should have
        self.speeds = speeds # a list of values detailing the animation speeds of each tile
        self.tilecount = len(self.index) # the number of tiles in a tile set

        # make the tiles
        self.tiles = [] # a list containing each tile in a tile set
        start_index = [0, 0] # stores the first animation frames index position of the current tile being created
        end_index   = [0, 0] # stores the last animation frames index of the current tile being created

        # creates each tile of the set
        for i in range(self.tilecount):

            # check if the tile needs to be animated or not
            if self.index[i] == 1: animated = False
            else: animated = True

            # determine the last frame of the tiles animation
            end_index[0] = (start_index[0] + self.index[i] - 1) % self.cols
            end_index[1] = start_index[1] + (start_index[0] + self.index[i] - 1) // self.cols

            # create tile and add it to the tile sheet
            self.tiles.append(Tile(self.img, start_index.copy(), end_index.copy(), animated, self.types[i], self.speeds[i]))

            # move to the next tile on the sheet
            start_index = end_index.copy()
            start_index[0] = (start_index[0] + 1) % self.cols
            if start_index[0] == 0: start_index[1] += 1

    def save(self, path):
        file = open(path, "wt")

        # write tilesheet path
        buffer = self.img_path + "\n"
        file.write(buffer)

        # write index data
        buffer = str(self.index).strip("[]").replace(" ", "") + "\n"
        file.write(buffer)

        # write types data
        buffer = str(self.types).strip("[]").replace(" ", "") + "\n"
        file.write(buffer)

        # write speeds data
        buffer = str(self.speeds).strip("[]").replace(" ", "") + "\n"
        file.write(buffer)

        file.close()

class Tilemap:

    def __init__(self, tilesheet, map):
        self.tilesheet = tilesheet
        self.map = map

    # uses all values in the tilemap to determine which tiles to draw
    # and dras them to the screen based on their index position in the
    # tilemap
    def draw(self, canvas):
        scroll =  game._game.camera.pos
        for i in range(self.tilesheet.tilecount):
            # resets the update flags on all tiles before drawing them
            self.tilesheet.tiles[i].updated = False

        # calculate visible region
        left = int(game._game.camera.pos.x)
        right = min(left + int(MAX_TILES_X) + 1, len(self.map[0]))

        top = int(game._game.camera.pos.y)
        bottom = min(top + int(MAX_TILES_Y) + 1, len(self.map))

        # draw tiles
        for y in range(top, bottom):
            for x in range(left, right):
                self.tilesheet.tiles[self.map[y][x]].draw(canvas, HALFSIZE + ((x - scroll.x) * TILESIZE), HALFSIZE + ((y - scroll.y) * TILESIZE))

    def save(self, path):
        file = open(path, "wt")

        # write tilesheet path
        buffer = self.tilesheet.img_path + "\n"
        file.write(buffer)

        # write index data
        buffer = str(self.tilesheet.index).strip("[]").replace(" ", "") + "\n"
        file.write(buffer)

        # write types data
        buffer = str(self.tilesheet.types).strip("[]").replace(" ", "") + "\n"
        file.write(buffer)

        # write speeds data
        buffer = str(self.tilesheet.speeds).strip("[]").replace(" ", "") + "\n"
        file.write(buffer)

        # writes the tile map data to the data file
        file.write("MAP_START\n")
        for y in range(len(self.map)):
            buffer = str(self.map[y]).strip("[]").replace(" ", "") + "\n"
            file.write(buffer)
        file.write("MAP_END\n")

        # closes the file
        file.close()

#TILE ENGINE UTILITY FUNCTIONS

# function for getting tiles
def get_tile(pos):
    tile_index = game._game.level.tilemap.map[pos.y][pos.x]
    return game._game.level.tilemap.tilesheet.tiles[tile_index]

# changes a specified "open_pit" tile to a "closed_pit" tile
def close_pit(pos):
    change_tile(pos, game._game.level.closed_pit)

# function which allows a tile at a given position on the tile
# map to be changhed into an entirley different tile
def change_tile(pos, tile):
    game._game.level.tilemap.map[pos.y][pos.x] = tile

# a function used for reading lines of comma separated data from files
# storing the individual data values as elements of a list
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

def load_tilesheet(path):
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

    # close the tilesheet file
    file.close()

    # create and return the new tilesheet
    tilesheet = Tilesheet(img_path, index[0], index[1], index[2])
    return tilesheet

def load_tilemap(path):

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

    # create a new tilemap and return it
    tilemap = Tilemap(tilesheet, map)
    return tilemap

