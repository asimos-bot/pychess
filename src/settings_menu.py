import pygame_menu
import settings


from player import RandomAI, Human
from piece import PieceColor
from game_board_controller import GameBoardController


class SettingsMenu:

    def __init__(self, dims: (int, int)):
        self.menu = pygame_menu.Menu(
                title='Settings',
                width=dims[0],
                height=dims[1],
                theme=pygame_menu.themes.THEME_BLUE
                )
        player_options = [('Random AI', RandomAI), ('Human', Human)]
        piece_colors = [('White', PieceColor.WHITE), ('Black', PieceColor.BLACK)]
        self.menu.add.selector(
                title='Player 1',
                items=player_options,
                default=1,
                style='fancy',
                onchange=(lambda _, y: self.set_player_type(1, y))
                )
        self.menu.add.selector(
                title='Player 2',
                items=player_options,
                default=0,
                style='fancy',
                onchange=(lambda _, y: self.set_player_type(2, y))
                )
        self.menu.add.selector(
                title='Player 1 Color',
                items=piece_colors,
                default=0,
                style='fancy',
                onchange=(lambda _, y: self.set_player1_color(y))
                )
        self.menu.add.button(
                title='Go Back',
                action=pygame_menu.events.BACK
                )

    def set_player_type(self, player_id, player_class):
        settings.PLAYER_TYPES[player_id] = player_class

    def set_player1_color(self, color):
        settings.PLAYER1_COLOR = color
        settings.PLAYER2_COLOR = GameBoardController.opposite_color(settings.PLAYER1_COLOR)

    def get_title(self):
        return self.menu.get_title()

    def resize(self, new_width, new_height):
        self.menu.resize(new_width, new_height)

    def update(self, surface, events):
        self.menu.draw(surface)
