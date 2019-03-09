try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import handlers
import game

# standard boilerplate code for creating a frame in simplguid
FRAMEWIDTH, FRAMEHEIGHT = 640, 480
frame = simplegui.create_frame("Sticky Situation", FRAMEWIDTH, FRAMEHEIGHT)
frame.set_draw_handler(game._game.draw)
frame.set_keydown_handler(handlers.keyboard.keydown)
frame.set_keyup_handler(handlers.keyboard.keyup)
frame.start()