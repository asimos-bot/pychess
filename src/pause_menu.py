import pygame_menu


class PauseMenu():
    def __init__(
            self,
            dims: (int, int),
            play_func,
            quit_func,
            restarting_func,
            orientation_func):
        self.menu = pygame_menu.Menu(
                title='PyChess',
                width=dims[0]/2,
                height=dims[1]/2,
                theme=pygame_menu.themes.THEME_BLUE)
        self.menu.add.button('Play', self.play)
        self.menu.add.button('Spin Board', self.orientation)
        self.menu.add.button('Restart', self.restarting)
        self.menu.add.button('Quit', self.quit)
        self.quit_func = quit_func
        self.play_func = play_func
        self.restarting_func = restarting_func
        self.orientation_func = orientation_func

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

    def resize(self, new_width, new_height):
        self.menu.resize(new_width, new_height)

    def update(self, surface, events):
        self.menu.update(events)
        self.menu.draw(surface)
