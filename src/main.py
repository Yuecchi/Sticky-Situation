try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

FRAMEWIDTH, FRAMEHEIGHT = 640, 480

import importlib
import handlers
import game

def make_frame():

    # standard boilerplate code for creating a frame in simplgui
    frame = simplegui.create_frame("Sticky Situation", FRAMEWIDTH, FRAMEHEIGHT)
    frame.set_draw_handler(game._game.draw)
    frame.set_keydown_handler(handlers.keyboard.keydown)
    frame.set_keyup_handler(handlers.keyboard.keyup)
    frame.set_mouseclick_handler(handlers.mouse.mouseclick)
    game.get_frame(frame)

    if game._game.state == game.GameState.EDITOR:
        game._game.change_state(game.GameState.TITLE)

    # displays text on the frame indiciating what the
    # controls of the game are
    frame.add_label("CONTROLS")
    frame.add_label("")
    frame.add_label("Press the WASD keys to move")
    frame.add_label("")
    frame.add_label("Press M to interact with")
    frame.add_label("buttons and levers")
    frame.add_label("")
    frame.add_label("Press P to open the menu")

    frame.start()

# THE WORLDS GREATEST HACK1!!
gotem = False
while True:

    make_frame()
    if game._game.close:
        break
    else:
        game._game.close = True

    if game._game.state == game.GameState.EDITOR:
        if not gotem:
            import levelEditor
            levelEditor.EDITOR_MUSIC.rewind()
            gotem = True
        else:
            importlib.reload(levelEditor)
            levelEditor.EDITOR_MUSIC.rewind()
        if game._game.close:
            break
        else:
            game._game.close = True
