import pygame_menu


class MainMenu():
    def __init__(self, dims: (int, int), play_func):
        self.menu = pygame_menu.Menu(
                title='Pychess',
                width=dims[0],
                height=dims[1],
                theme=pygame_menu.themes.THEME_BLUE)
        self.menu.add.button(
                'Play',
                self.play)
        self.menu.add.button(
                'Quit',
                pygame_menu.events.EXIT)
        self.play_func = play_func

    def play(self):
        self.play_func()

    def resize(self, new_width, new_height):
        self.menu.resize(new_width, new_height)

    def update(self, surface, events):
        self.menu.update(events)
        self.menu.draw(surface)
