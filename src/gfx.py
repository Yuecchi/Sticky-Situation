import game

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
    game.player.draw(canvas)
    game.block.draw(canvas)

    for i in range(len(game.e_map)):
        canvas.draw_text(str(game.e_map[i]), (400, 16 + (i * 16)), 16, "White")

    clock.tick()



