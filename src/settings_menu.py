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
                title='Go Back',
                action=pygame_menu.events.BACK
                )

    def set_player_type(self, player_color, player_class):
        settings.PLAYERS[player_color] = player_class
        if settings.PLAYERS[PieceColor.WHITE] == Human:
            settings.BOARD_INITIAL_BOTTOM_COLOR = PieceColor.WHITE
        elif settings.PLAYERS[PieceColor.BLACK] == Human:
            settings.BOARD_INITIAL_BOTTOM_COLOR = PieceColor.BLACK
        else:
            # two AIs
            settings.BOARD_INITIAL_BOTTOM_COLOR = PieceColor.WHITE

    def get_title(self):
        return self.menu.get_title()

    def resize(self, new_width, new_height):
        self.menu.resize(new_width, new_height)

    def update(self, surface, events):
        self.menu.draw(surface)
