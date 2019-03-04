import game

TILESIZE = 32
HALFSIZE = 16

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
        self.cols = self.img.get_width() / TILESIZE
        self.animation = ((0, 0), (0, 0))
        self.current_frame = self.animation[0].copy()

    def draw(self, canvas):
        #canvas.draw_image(image, center_source, width_height_source, center_dest, width_height_dest)
        pass


clock = Clock()

def draw(canvas):

    global clock

    game.tilemap.draw(canvas)

    clock.tick()



