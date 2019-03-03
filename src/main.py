try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

import gfx

# standard boilerplate code for creating a frame in simplgui
FRAMEWIDTH, FRAMEHEIGHT = 640, 480
frame = simplegui.create_frame("Stick Situation", FRAMEWIDTH, FRAMEHEIGHT)
frame.set_draw_handler(gfx.draw)
frame.start()

