from enum import IntEnum
import game

TILESIZE = 32
HALFSIZE = 16
TILE_DIMS = (TILESIZE, TILESIZE)

class TileType(IntEnum):

    EMPTY          = 0 # any regular tile which can be stepped on
    SOLID          = 1 # any regular tile which acts as a wall
    ICY            = 2 # tiles which make the player slide
    LEFT_FENCE     = 3 # tiles which can be jumped over from the right
    RIGHT_FENCE    = 4 # tile which can be jumped over from the left
    CONVEYOR_UP    = 5
    CONVEYOR_LEFT  = 6
    CONVEYOR_DOWN  = 7
    CONVEYOR_RIGHT = 8

class Tile:

    def __init__(self, img, start_index, end_index, animated, type, speed):

        # reference of the tilesheet from the containing tilesheet class
        self.img = img
        self.cols = self.img.get_width() // TILESIZE

        self.type = type

        self.start_index = start_index
        self.end_index = end_index
        self.current_index = self.start_index.copy()

        self.animated = animated
        self.animation_speed = speed
        self.updated = False

    def set_animation_speed(self, speed):
        self.animation_speed = speed

    def draw(self, canvas, x, y):
        pos = (x, y)
        src_pos = (HALFSIZE + (self.current_index[0] * TILESIZE), HALFSIZE +  (self.current_index[1] * TILESIZE))
        canvas.draw_image(self.img, src_pos, TILE_DIMS, pos, TILE_DIMS)
        # checks if this tile animation has already been updated
        if not self.updated:
            if self.animated:
                if game._game.clock.transition(self.animation_speed):
                    self.nextFrame()
                    # sets the updated flag to true so avoid extra updates
                    self.updated = True

    def nextFrame(self):
        if self.current_index == self.end_index:
            self.current_index = self.start_index.copy()
        else:
            self.current_index[0] = (self.current_index[0] + 1) % self.cols
            if self.current_index[0] == 0: self.current_index[1] += 1

class Tilesheet:

    def __init__(self, img, index, types, speeds):

        # source image for tile sheet
        self.img = img

        # automatically assumes the number of tiles in the tilesheet
        # based on the sheets dimensions and the tilesize
        self.cols = self.img.get_width() // TILESIZE

        self.index = index
        self.types = types
        self.speeds = speeds
        self.tilecount = len(self.index)

        # make the tiles
        self.tiles = []
        start_index = [0, 0]
        end_index   = [0, 0]
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
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                self.tilesheet.tiles[self.map[y][x]].draw(canvas, HALFSIZE + ((x - scroll.x) * TILESIZE), HALFSIZE + ((y - scroll.y) * TILESIZE))

# function for getting tiles
def get_tile(pos):
    tile_index = game._game.level.tilemap.map[pos.y][pos.x]
    return game._game.level.tilemap.tilesheet.tiles[tile_index]

