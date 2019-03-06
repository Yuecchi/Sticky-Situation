try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import gfx
import handlers

# standard boilerplate code for creating a frame in simplgui
FRAMEWIDTH, FRAMEHEIGHT = 640, 480
frame = simplegui.create_frame("Sticky Situation", FRAMEWIDTH, FRAMEHEIGHT)
frame.set_draw_handler(gfx.draw)
frame.set_keyup_handler(handlers.keyup)
frame.set_keydown_handler(handlers.keydown)
frame.start()

