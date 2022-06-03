import pygame_menu


class PauseMenu():
    def __init__(
            self,
            pos: (int, int),
            dims: (int, int),
            play_func,
            quit_func,
            restarting_func,
            orientation_func):
        self.menu = pygame_menu.Menu(
                title='PyChess',
                width=dims[0],
                height=dims[1],
                theme=pygame_menu.themes.THEME_BLUE)
        self.menu.add.button('Play', self.play)
        self.menu.add.button('Spin Board', self.orientation)
        self.menu.add.button('Restart', self.restarting)
        self.menu.add.button('Quit', self.quit)
        self.quit_func = quit_func
        self.play_func = play_func
        self.restarting_func = restarting_func
        self.orientation_func = orientation_func

        self.resize(pos, dims)

    def play(self):
        self.menu.close()
        self.play_func()

    def quit(self):
        self.menu.close()
        self.quit_func()

    def restarting(self):
        self.restarting_func()
        self.menu.close()

    def orientation(self):
        self.orientation_func()

    def resize(self, coords, size):
        self.menu.resize(size[0], size[1])
        self.menu.set_absolute_position(coords[0], coords[1])

    def update(self, surface, events):
        self.menu.update(events)
        self.menu.draw(surface)
