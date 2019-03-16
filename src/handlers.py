try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

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

class Keyboard:

    def __init__(self):

        self.w = False
        self.a = False
        self.s = False
        self.d = False
        self.m = False

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

keyboard = Keyboard()