from matplotlib.pyplot import margins
import pygame_menu


class MainMenu():
    def __init__(self, dims: (int, int), play_func):
        main_menu_theme = pygame_menu.themes.THEME_ORANGE.copy()
        main_menu_theme.set_background_color_opacity(0.5)  # 50% opacity
        theme_bg_image = main_menu_theme.copy()
        theme_bg_image.background_color = pygame_menu.BaseImage(
            image_path="../assets/bg.png"
        )
        self.menu = pygame_menu.Menu(
                title='',
                width=dims[0],
                height=dims[1],
                theme=theme_bg_image)
        self.menu.get_menubar().hide()
        self.menu.add.button('Play', self.play, align=pygame_menu.locals.ALIGN_RIGHT, margin = (10,0))
        self.menu.add.button('Quit', pygame_menu.events.EXIT, align=pygame_menu.locals.ALIGN_RIGHT, margin = (10,0))
        self.play_func = play_func

    def play(self):
        self.play_func()

    def resize(self, new_width, new_height):
        self.menu.resize(new_width, new_height)

    def update(self, surface, events):
        self.menu.update(events)
        self.menu.draw(surface)
