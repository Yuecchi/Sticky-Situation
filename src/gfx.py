import game

def draw(canvas):
    game.tilesheet.draw(canvas)
    #game.tilesheet.tiles[1].draw(canvas, 48, 48)

    canvas.draw_text(str(game.tilesheet.tiles[0].current_index), (0, 32), 16, "White")
    canvas.draw_text(str(game.tilesheet.tiles[1].current_index), (0, 48), 16, "White")
    canvas.draw_text(str(game.tilesheet.tiles[2].current_index), (0, 64), 16, "White")
    canvas.draw_text(str(game.tilesheet.tiles[3].current_index), (0, 80), 16, "White")

