try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from tileEngine import Tilesheet

# testing tilesheets
img = simplegui.load_image('https://i.imgur.com/1v3BBoO.png')
index = (1, 1, 10, 1)
tilesheet = Tilesheet(img, index)




