try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from vectors import Vector

class Menu:

    def __init__(self):

        self.options = []

    def add_option(self, option):
        self.options.append(option)

    def update(self, mouse):
        # check if any options have been clicked
        if len(self.options) != 0:
            for option in self.options:
                option.update(mouse)

    def display(self, canvas):
        if len(self.options) != 0:
            for option in self.options:
                option.draw(canvas)

class Option:

    def __init__(self, pos, unselected_img, selected_img):

        self.pos = pos
        self.selected = False
        self.action = None

        self.unselected_img = unselected_img
        self.selected_img = selected_img

        self.dims = (self.unselected_img.get_width(), self.unselected_img.get_height())
        self.half_dims = (self.dims[0] / 2, self.dims[1] / 2)

    def set_action(self, action):
        self.action = action

    def check_cursor(self, m_pos):
        if m_pos.x < self.pos.x - self.half_dims[0]: return False
        elif m_pos.x > self.pos.x + self.half_dims[0]: return False
        elif m_pos.y < self.pos.y - self.half_dims[1]: return False
        elif m_pos.y > self.pos.y + self.half_dims[1]: return False
        else:
            return True

    def update(self, mouse):
        # if mouse is clicked
        if mouse.clicked:
            # if mouse is inside option
            if self.check_cursor(Vector(mouse.pos)):
                # perform action
                self.selected = not self.selected
                self.action()

    def draw(self, canvas):

        if not self.selected:
            canvas.draw_image(self.unselected_img, self.half_dims, self.dims, self.pos.getP(), self.dims)
        else:
            canvas.draw_image(self.selected_img, self.half_dims, self.dims, self.pos.getP(), self.dims)

unselected_img = simplegui._load_local_image("../assets/title_menu/start_button_unselected.png")
selected_img = simplegui._load_local_image("../assets/title_menu//start_button_selected.png")
option_start = Option(Vector((170, 400)), unselected_img, selected_img)

unselected_img = simplegui._load_local_image("../assets/title_menu//quit_button_unselected.png")
selected_img = simplegui._load_local_image("../assets/title_menu//quit_button_selected.png")
option_quit = Option(Vector((460, 400)), unselected_img, selected_img)

title_menu = Menu()
title_menu.add_option(option_start)
title_menu.add_option(option_quit)