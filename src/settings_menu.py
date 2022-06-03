import pygame_menu


from player import RandomAI, Human
from piece import PieceColor


class SettingsMenu:

    def __init__(self, dims: (int, int), settings: dict()):
        self.settings = settings
        self.menu = pygame_menu.Menu(
                title='Settings',
                width=dims[0],
                height=dims[1],
                theme=pygame_menu.themes.THEME_BLUE
                )
        player_options = [
                ('Random AI', RandomAI),
                ('Human', Human)]
        default_white = player_options.index(next(filter(
                lambda x: x[1] == settings['players'][PieceColor.WHITE],
                player_options)))
        default_black = player_options.index(next(filter(
                lambda x: x[1] == settings['players'][PieceColor.BLACK],
                player_options)))

        self.menu.add.dropselect(
                title='White controller',
                items=player_options,
                default=default_white,
                onchange=(
                    lambda _, y: self.set_player_type(PieceColor.WHITE, y))
                )
        self.menu.add.dropselect(
                title='Black controller',
                items=player_options,
                default=default_black,
                onchange=(
                    lambda _, y: self.set_player_type(PieceColor.BLACK, y))
                )

        for k in self.settings['colors']:
            self.add_color_picker(
                    setting_name=k,
                    color_setting_dict=self.settings['colors'])
        self.menu.add.button(
                title='Go back to main menu',
                action=pygame_menu.events.BACK
                )

    def add_color_picker(self, setting_name, color_setting_dict):
        title = setting_name.lower().replace('_', ' ').capitalize()
        title += ' color'
        self.menu.add.color_input(
                title=title,
                color_type=pygame_menu.widgets.COLORINPUT_TYPE_RGB,
                default=color_setting_dict[setting_name],
                onchange=(
                    lambda x: self.set_color(
                        setting_name,
                        color_setting_dict,
                        x)))

    def set_color(self, setting_name, color_setting_dict, value):
        if -1 not in value:
            color_setting_dict[setting_name] = value

    def set_player_type(self, player_color, player_class):
        self.settings['players'][player_color] = player_class
        if self.settings['players'][PieceColor.WHITE] == Human:
            self.settings['initial_bottom_color'] = PieceColor.WHITE
        elif self.settings['players'][PieceColor.BLACK] == Human:
            self.settings['initial_bottom_color'] = PieceColor.BLACK
        else:
            # two AIs
            self.settings['initial_bottom_color'] = PieceColor.WHITE

    def get_title(self):
        return self.menu.get_title()

    def resize(self, new_width, new_height):
        self.menu.resize(new_width, new_height)

    def update(self, surface, events):
        self.menu.draw(surface)
