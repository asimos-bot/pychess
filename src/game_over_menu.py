import pygame_menu


class GameOverMenu:
    def __init__(self, dims: (int, int), quit_func, restarting_func, title, message):
        self.menu = pygame_menu.Menu(
            title=title,
            width=dims[0]/2,
            height=dims[1]/2,
            theme=pygame_menu.themes.THEME_BLUE)

        self.menu.add.button('Restart', self.restarting)
        self.menu.add.button('Quit', self.quit)

        self.quit_func = quit_func
        self.restarting_func = restarting_func

    def restarting(self):
        self.restarting_func()
        self.menu.close()

    def quit(self):
        self.restarting_func()
        self.menu.close()

    def resize(self, new_width, new_height):
        self.menu.resize(new_width, new_height)

    def update(self, surface, events):
        self.menu.update(events)
        self.menu.draw(surface)
