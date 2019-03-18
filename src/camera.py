from vectors import Vector
import tileEngine

FRAMEWIDTH, FRAMEHEIGHT = 640, 480
TILESIZE = tileEngine.TILESIZE
MAX_TILES_X = FRAMEWIDTH / TILESIZE
MAX_TILES_Y = FRAMEHEIGHT / TILESIZE

MIN_SCROLL_X = int((FRAMEWIDTH / 2) / TILESIZE)
MIN_SCROLL_Y = int((FRAMEHEIGHT / 2) / TILESIZE)

class Camera:

    def __init__(self):

        self.pos = Vector()
        self.anchor = None
        self.max_scroll = None

    def set_camera_pos(self,x, y):
        self.pos.x = x
        self.pos.y = y

    def set_anchor(self, anchor):
        self.anchor = anchor

    def set_max_scroll(self, tilemap):
        self.max_scroll = Vector()
        self.max_scroll.x = max(0, len(tilemap.map[0]) - MAX_TILES_X)
        self.max_scroll.y = max(0, len(tilemap.map) - MAX_TILES_Y)

    def update(self):
        # if the current levels map does not exceed the dimensions of the
        # canvas, it will never need to scroll
        self.pos.x = self.anchor.pos.x - MIN_SCROLL_X
        self.pos.y = self.anchor.pos.y - MIN_SCROLL_Y

        if self.anchor.pos.x < MIN_SCROLL_X:
            self.pos.x = 0
        if self.pos.x > self.max_scroll.x:
            self.pos.x = self.max_scroll.x

        if self.anchor.pos.y < MIN_SCROLL_Y:
            self.pos.y = 0
        if self.pos.y > self.max_scroll.y:
            self.pos.y = self.max_scroll.y
