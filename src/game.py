try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from vectors import Vector
from tileEngine import Tilesheet
from tileEngine import Tilemap
from entities   import Player

# testing tilesheets
img = simplegui.load_image('https://i.imgur.com/1v3BBoO.png')
index = (1, 1, 10, 1)

tilesheet = Tilesheet(img, index)
tilesheet.tiles[2].set_animation_speed(8)

map = [[2, 3, 2, 3, 2],
       [3, 0, 1, 0, 3],
       [2, 1, 2, 1, 2],
       [3, 0, 1, 0, 3],
       [2, 3, 2, 3, 2]]

tilemap = Tilemap(tilesheet, map)
player = Player(Vector((4, 3)))






