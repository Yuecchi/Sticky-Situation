try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from vectors import Vector
from tileEngine import Tilesheet
from tileEngine import Tilemap
from entities   import Player
from entities   import  Sprite


# testing tilesheets
#img = simplegui.load_image('https://i.imgur.com/1v3BBoO.png')
# testsheet = simplegui._load_local_image('../assets/testsheet2.png')
testsheet = simplegui._load_local_image('../assets/testsheet.png')
testsprite = simplegui._load_local_image('../assets/testsprite.png')

index = (1, 1, 10, 1)
#index = (36, 1, 6, 6, 3, 3, 3)

tilesheet = Tilesheet(testsheet, index)
tilesheet.tiles[2].set_animation_speed(8)

t_map = [
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 0, 0, 0, 3, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 3, 0, 3, 0, 0, 3],
    [3, 3, 3, 3, 3, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
]

e_map = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

# could have a unique identifier attatched to each entity
# which also links to to a class for whichg entity type it is

tilemap = Tilemap(tilesheet, t_map)
player = Player(Vector((1, 1)), testsprite)






