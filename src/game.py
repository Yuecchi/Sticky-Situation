try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from tileEngine import Tilesheet
from tileEngine import Tilemap

# testing tilesheets
img = simplegui.load_image('https://i.imgur.com/1v3BBoO.png')
index = (1, 1, 10, 1)

tilesheet = Tilesheet(img, index)
tilesheet.tiles[2].set_animation_speed(6)

map = [[3, 3, 3, 3, 3],
       [3, 0, 1, 0, 3],
       [3, 1, 2, 1, 3],
       [3, 0, 1, 0, 3],
       [3, 3, 3, 3, 3]]

tilemap = Tilemap(tilesheet, map)






