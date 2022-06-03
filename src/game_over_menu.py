import pygame_menu


class GameOverMenu:
    def __init__(
            self,
            dims: (int, int),
            quit_func,
            restarting_func,
            settings,
            title,
            message):
        self.menu = pygame_menu.Menu(
            title=title,
            width=dims[0]/2,
            height=dims[1]/2,
            theme=pygame_menu.themes.THEME_BLUE)

        self.menu.add.label(title=message)
        self.menu.add.button('Restart', self.restarting)
        self.menu.add.button('Quit', self.quit)

        self.quit_func = quit_func
        self.restarting_func = restarting_func
        self.settings = settings

        self.resize(dims[0], dims[1])

    def restarting(self):
        self.restarting_func()
        self.menu.close()

    def quit(self):
        self.quit_func()
        self.menu.close()

    def resize(self, new_width, new_height):
        dims = (new_width, new_height)

        top_spacing_percentage = self.settings['top_spacing_percentage']
        right_spacing_percentage = self.settings['right_spacing_percentage']
        # get lowest dimension to define sizes
        self.tile_side = min(
                dims[0] * (1 - right_spacing_percentage),
                dims[1] * (1 - top_spacing_percentage))/10

        # get coordinates that fit inside space given
        middle_point = dims[1] * (1 + top_spacing_percentage)/2

        self.coords = (
                10 * self.tile_side,
                middle_point - 5 * self.tile_side)

        self.menu.resize(dims[0] - self.coords[0], self.tile_side * 10)
        self.menu.set_absolute_position(self.coords[0], self.coords[1])

    def update(self, surface, events):
        self.menu.update(events)
        self.menu.draw(surface)
