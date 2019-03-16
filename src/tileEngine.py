from enum import Enum
import gfx

FRAMEWIDTH, FRAMEHEIGHT = 640, 480

TILESIZE = 32
HALFSIZE = 16
TILE_DIMS = (TILESIZE, TILESIZE)


class Tiletype(Enum):
    EMPTY = 0
    SOLID = 1
    ICY   = 2


class Tile:

    def __init__(self, img, start_index, end_index, animated):

        # reference of the tilesheet from the containing tilesheet class
        self.img = img
        self.cols = self.img.get_width() // TILESIZE

        self.start_index = start_index
        self.end_index = end_index
        self.current_index = self.start_index.copy()

        self.animated = animated
        self.animation_speed = 1
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
                if gfx.clock.transition(self.animation_speed):
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

    def __init__(self, img, index):

        # source image for tile sheet
        self.img = img

        # automatically assumes the number of tiles in the tilesheet
        # based on the sheets dimensions and the tilesize
        self.cols = self.img.get_width() // TILESIZE

        self.index = index
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
            end_index[1] = start_index[1] + ((start_index[0] + self.index[i] - 1) // self.cols)

            # create tile and add it to the tile sheet
            self.tiles.append(Tile(self.img, start_index.copy(), end_index.copy(), animated))

            # move to the next tile on the sheet
            start_index = end_index.copy()
            start_index[0] = (start_index[0] + 1) % self.cols
            if start_index[0] == 0: start_index[1] += 1

    def draw(self, canvas):
        width, height = self.img.get_width(), self.img.get_height()
        pos = (width, height)
        center = (width / 2 , height / 2)
        canvas.draw_image(self.img, center, pos, (FRAMEWIDTH / 2, FRAMEHEIGHT / 2), pos)


class Tilemap:

    def __init__(self, tilesheet, map):
        self.tilesheet = tilesheet
        self.map = map

    def draw(self, canvas):
        for i in range(self.tilesheet.tilecount):
            # resets the update flags on all tiles before drawing them
            self.tilesheet.tiles[i].updated = False
        for y in range(len(self.map)):
            for x in range(len(self.map[0])):
                self.tilesheet.tiles[self.map[y][x]].draw(canvas, HALFSIZE + (x * TILESIZE), HALFSIZE + (y * TILESIZE))

