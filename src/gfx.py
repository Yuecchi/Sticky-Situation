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

clock = Clock()


def draw(canvas):

    global clock

    game.tilemap.draw(canvas)

    clock.tick()



