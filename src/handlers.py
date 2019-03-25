try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

# standard mouse evenent handler class, contains a tuple which stores the
# cursor position of the mouse, and a reset method for setting the mouse buttons
# back to being "unclicked" when called

class Mouse:

    def __init__(self):
        self.pos = (0, 0)
        self.reset()

    def mouseclick(self, pos):
        self.pos = pos
        self.clicked = True

    def reset(self):
        self.clicked = False

mouse = Mouse()

# a standard keyboard event handler class. Includes boolean flags for each of the
# keys used in the game, and methods for detecting when keys are pressed and released

class Keyboard:

    def __init__(self):

        self.w = False
        self.a = False
        self.s = False
        self.d = False
        self.m = False
        self.p = False

    # when a key is pressed, the flag attached to which key it is is set to true
    def keydown(self, key):

        if key == simplegui.KEY_MAP['w']:
            self.w = True
        if key == simplegui.KEY_MAP['a']:
            self.a = True
        if key == simplegui.KEY_MAP['s']:
            self.s = True
        if key == simplegui.KEY_MAP['d']:
            self.d = True
        if key == simplegui.KEY_MAP['m']:
            self.m = True
        if key == simplegui.KEY_MAP['p']:
            self.p = True

    # when a key is released, the flag attached to which key it is is set to false
    def keyup(self, key):

        if key == simplegui.KEY_MAP['w']:
            self.w = False
        if key == simplegui.KEY_MAP['a']:
            self.a = False
        if key == simplegui.KEY_MAP['s']:
            self.s = False
        if key == simplegui.KEY_MAP['d']:
            self.d = False
        if key == simplegui.KEY_MAP['m']:
            self.m = False
        if key == simplegui.KEY_MAP['p']:
            self.p = False

keyboard = Keyboard()