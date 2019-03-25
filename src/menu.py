try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

from vectors import Vector

# class for bulding in game menus
class Menu:

    def __init__(self):

        # menus contain a list of selectable options
        # list currently empty list can be populate with options
        # which will be selectable when the menu is active
        self.options = []

    # method of adding a new option to the menu
    def add_option(self, option):
        self.options.append(option)

    # method which checks if any of the options attatched to the manu
    # have been interacted with
    def update(self, mouse):
        # check if any options have been clicked
        if len(self.options) != 0:
            for option in self.options:
                option.update(mouse)

    # draws the menu's options buttons
    def display(self, canvas):
        if len(self.options) != 0:
            for option in self.options:
                option.draw(canvas)

# creates selectedable options for menus
# these are buttons which can be interacted with using the mouse
# and can have any function attatched to them
class Option:

    def __init__(self, pos, unselected_img, selected_img):


        self.pos = pos  # the placement of the button on the canvas
        self.selected = False # keeps track of whether or not the option has been selected
        self.action = None # a function which is executed when the option is selected

        self.unselected_img = unselected_img # the image which displays before the option has been clicked on
        self.selected_img = selected_img # the image whcih displays after the options has been clicked on

        # uses the dimensions of the graphic of the "unselected" graphic to determine the
        # dimensions of the button for which it will respond if the cursor is inside
        self.dims = (self.unselected_img.get_width(), self.unselected_img.get_height())

        # pre calculation for reducing the number of calculations necessary for cursor detection later
        self.half_dims = (self.dims[0] / 2, self.dims[1] / 2)

    # method which attached a function to the option
    def set_action(self, action):
        self.action = action

    # method which checks if the option has been clicked on
    def check_cursor(self, m_pos):
        if m_pos.x < self.pos.x - self.half_dims[0]: return False
        elif m_pos.x > self.pos.x + self.half_dims[0]: return False
        elif m_pos.y < self.pos.y - self.half_dims[1]: return False
        elif m_pos.y > self.pos.y + self.half_dims[1]: return False
        else:
            return True

    # performs checks every frame to determine whether or not the options has been selected
    def update(self, mouse):
        # if mouse is clicked
        if mouse.clicked:
            # if mouse is inside option
            if self.check_cursor(Vector(mouse.pos)):
                # perform action
                self.selected = not self.selected
                self.action()

    # drawns the graphics for the option
    def draw(self, canvas):

        if not self.selected:
            canvas.draw_image(self.unselected_img, self.half_dims, self.dims, self.pos.getP(), self.dims)
        else:
            canvas.draw_image(self.selected_img, self.half_dims, self.dims, self.pos.getP(), self.dims)

# BUILDING THE TITLE SCREEN MENU
unselected_img = simplegui._load_local_image("../assets/menus/title_menu/start_button.png")
selected_img   = unselected_img
option_start = Option(Vector((109, 400)), unselected_img, selected_img)

unselected_img = simplegui._load_local_image("../assets/menus/title_menu/editor_button.png")
selected_img   = unselected_img
option_editor = Option(Vector((320, 400)), unselected_img, selected_img)

unselected_img = simplegui._load_local_image("../assets/menus/title_menu/quit_button.png")
selected_img   = unselected_img
option_quit = Option(Vector((530, 400)), unselected_img, selected_img)

title_menu = Menu()
title_menu.add_option(option_start)
title_menu.add_option(option_editor)
title_menu.add_option(option_quit)

# BUILDING THE IN GAME PAUSE SCREEN MENU
unselected_img = simplegui._load_local_image("../assets/menus/pause_menu/resume_button.png")
selected_img   = unselected_img
option_resume = Option(Vector((109, 270)), unselected_img, selected_img)

unselected_img = simplegui._load_local_image("../assets/menus/pause_menu/retry_button.png")
selected_img   = unselected_img
option_retry = Option(Vector((320, 270)), unselected_img, selected_img)

unselected_img = simplegui._load_local_image("../assets/menus/pause_menu/quit_button.png")
selected_img   = unselected_img
option_to_title = Option(Vector((530, 270)), unselected_img, selected_img)

pause_menu = Menu()
pause_menu.add_option(option_resume)
pause_menu.add_option(option_retry)
pause_menu.add_option(option_to_title)