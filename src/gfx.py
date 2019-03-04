import game
import math

TILESIZE = 32
HALFSIZE = 16

def draw(canvas):
    game.tilesheet.draw(canvas)

    for i in range(game.tilesheet.tilecount):
        game.tilesheet.tiles[i].draw(canvas, HALFSIZE + (TILESIZE * i), HALFSIZE)

    canvas.draw_text(str(game.tilesheet.tiles[2].current_index), (0, 64), 16, "White")

    for i in range(1000000):
        math.sqrt(2)



