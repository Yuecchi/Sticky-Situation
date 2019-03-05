import game

TILESIZE = 32
HALFSIZE = 16
TILE_DIMS = (TILESIZE, TILESIZE)

class Clock:

    def __init__(self):
        self.t = 0

    def tick(self):
        self.t += 1

    def transition(self, rate):
        return not(self.t % rate)

class Sprite:

    def __init__(self, img):

        self.img = img
        self.animation = ((0, 0), (0, 0))
        self.current_index = (0, 0)

    def draw(self, canvas, x, y):
        pos = (x, y)
        src_pos = (HALFSIZE + (self.current_index[0] * TILESIZE), HALFSIZE + (self.current_index[1] * TILESIZE))
        canvas.draw_image(self.img, src_pos, TILE_DIMS, pos, TILE_DIMS)

clock = Clock()

def draw(canvas):

    global clock

    game.tilemap.draw(canvas)

    clock.tick()



