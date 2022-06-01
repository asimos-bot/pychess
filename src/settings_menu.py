import pygame_menu


from player import RandomAI, Human
from piece import PieceColor
from game_board_controller import GameBoardController


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
        self.menu.add.selector(
                title='White Controller',
                items=player_options,
                default=1,
                style='fancy',
                onchange=(
                    lambda _, y: self.set_player_type(PieceColor.WHITE, y))
                )
        self.menu.add.selector(
                title='Black Controller',
                items=player_options,
                default=0,
                style='fancy',
                onchange=(
                    lambda _, y: self.set_player_type(PieceColor.BLACK, y))
                )
        self.menu.add.button(
                title='Go Back to Main Menu',
                action=pygame_menu.events.BACK
                )

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
