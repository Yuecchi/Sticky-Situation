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

    game.tilesheet.draw(canvas)
    game.tilemap.draw(canvas)

    #for i in range(game.tilesheet.tilecount):
    #    game.tilesheet.tiles[i].draw(canvas, HALFSIZE + (TILESIZE * i), HALFSIZE)
    #canvas.draw_text(str(game.tilesheet.tiles[2].current_index), (0, 64), 16, "White")

    clock.tick()



