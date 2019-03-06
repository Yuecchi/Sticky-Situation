try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from vectors import Vector
from tileEngine import Tilesheet
from tileEngine import Tilemap
from entities   import Player
from entities   import PushBlock

# testing tilesheets
testsheet = simplegui._load_local_image('../assets/testsheet.png')
testsprite = simplegui._load_local_image('../assets/testsprite.png')
testblock = simplegui._load_local_image('../assets/testblock.png')

index = (1, 1, 10, 1)
types = (0, 0, 1 , 1)

tilesheet = Tilesheet(testsheet, index, types)
tilesheet.tiles[2].set_animation_speed(8)

t_map = [
    [2, 3, 3, 3, 3, 3, 3, 3, 3, 2],
    [3, 0, 0, 0, 3, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 3, 0, 3, 0, 0, 3],
    [3, 3, 3, 3, 3, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 3, 0, 0, 3],
    [3, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [2, 3, 3, 3, 3, 3, 3, 3, 3, 2],
]

tilemap = Tilemap(tilesheet, t_map)

# testing entities
e_map = [
    [
        0 for x in range(len(t_map[0]))
    ] for y in range(len(t_map))
]

player = Player(Vector((1, 1)), testsprite, e_map, tilemap)
block  = PushBlock(Vector((3, 6)), testblock, e_map, tilemap)






