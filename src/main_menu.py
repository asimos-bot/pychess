import pygame_menu

from settings_menu import SettingsMenu


class MainMenu:

    def __init__(self, dims: (int, int), play_func, settings: dict()):
        self.settings = SettingsMenu(dims, settings)

        self.menu = pygame_menu.Menu(
                title='Pychess',
                width=dims[0],
                height=dims[1],
                theme=pygame_menu.themes.THEME_BLUE)
        self.menu.add.button(
                'Play',
                self.play)
        self.menu.add.button(
                self.settings.get_title(),
                self.settings.menu
                )
        self.menu.add.button(
                'Quit',
                pygame_menu.events.EXIT,
                )
        self.play_func = play_func

    def play(self):
        self.play_func()

    def resize(self, new_width, new_height):
        self.menu.resize(new_width, new_height)
        self.settings.resize(new_width, new_height)

    def update(self, surface, events):
        self.menu.update(events)
        self.settings.update(surface, events)
        self.menu.draw(surface)
