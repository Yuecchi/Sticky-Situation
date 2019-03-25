from vectors import Vector
import tileEngine

FRAMEWIDTH, FRAMEHEIGHT = 640, 480 # canvas width and size
TILESIZE = tileEngine.TILESIZE # 32x32, the size of every tile in the game

# the maximum number of columns of tiles displayable on screen with the current canvas width
MAX_TILES_X = FRAMEWIDTH / TILESIZE
# the maximum number of rows of tiles displayable on screen with the current canvas height
MAX_TILES_Y = FRAMEHEIGHT / TILESIZE

# constants indicating where the camera
# should stop scrolling to the left / up
MIN_SCROLL_X = int((FRAMEWIDTH / 2) / TILESIZE)
MIN_SCROLL_Y = int((FRAMEHEIGHT / 2) / TILESIZE)


# the camera class is responsible for keeping track of what portion of the map should
# currently be visible on the canvas. the camera allows the screen to scroll
class Camera:

    def __init__(self):

        self.pos = Vector() # stores the location of the camera
        self.anchor = None # stores an entity which the camera will follow
        self.max_scroll = None # a vector indicating when the camera will stop scrolling right / down

    # a method allowing the camera to snap to a target location
    def set_camera_pos(self,x, y):
        self.pos.x = x
        self.pos.y = y

    # a method which sets an entity as the cameras anchor, setting that
    # entity as the object which the camera will follow and center around
    def set_anchor(self, anchor):
        self.anchor = anchor

    # a method which sets the maximum scroll value for the camera. This determines how far the camera will
    # go down / to the right before it stop scrolling. This limit is determined by the size of the current levels
    # tile map
    def set_max_scroll(self, tilemap):
        self.max_scroll = Vector()
        self.max_scroll.x = max(0, len(tilemap.map[0]) - MAX_TILES_X)
        self.max_scroll.y = max(0, len(tilemap.map) - MAX_TILES_Y)

    # the update method for the camera simply moves the camera based on the position of the anchor
    def update(self):
        # if the current levels map does not exceed the dimensions of the
        # canvas, it will never need to scroll
        self.pos.x = self.anchor.pos.x - MIN_SCROLL_X
        self.pos.y = self.anchor.pos.y - MIN_SCROLL_Y

        # keeps track of the x position of the anchor to ensure it can't scroll
        # too far left or too far right, so it never leave the confines of the current
        # levels tile map
        if self.anchor.pos.x < MIN_SCROLL_X:
            self.pos.x = 0
        if self.pos.x > self.max_scroll.x:
            self.pos.x = self.max_scroll.x

        # keeps track of the y position of the anchor to ensure it can't scroll
        # too far top or too far bottom, so it never leave the confines of the current
        # levels tile map
        if self.anchor.pos.y < MIN_SCROLL_Y:
            self.pos.y = 0
        if self.pos.y > self.max_scroll.y:
            self.pos.y = self.max_scroll.y
