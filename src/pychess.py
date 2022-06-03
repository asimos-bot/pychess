#!/usr/bin/env python3
import pygame
import pygame.locals
from enum import Enum

from game_board import GameBoard
from main_menu import MainMenu
from pause_menu import PauseMenu
from game_over_menu import GameOverMenu
from piece import PieceDrawer, PieceColor
from player import Human, RandomAI


class GameState(Enum):
    MAIN_MENU = 1
    PAUSE = 2
    QUIT = 3
    PLAY = 4
    GAME_OVER = 5


class PyChess():
    def __init__(self):
        pygame.init()
        # get surface where we will draw stuff to
        self.surface = pygame.display.set_mode((600, 400), pygame.RESIZABLE)

        # settings
        self.settings = {
                'players': {
                    PieceColor.WHITE: Human,
                    PieceColor.BLACK: RandomAI
                    },
                'initial_bottom_color': PieceColor.WHITE,
                'top_spacing_percentage': 0.2,
                'right_spacing_percentage': 0.3,
                'colors': {
                    'clear_screen': (128, 128, 128),
                    'game_board': (24, 240, 128),
                    'piece_selection': (250, 12, 12),
                    'valid_move': (32, 255, 32)
                    }
                }

        # load piece images
        PieceDrawer.load_images()

        self.x, self.y = self.surface.get_size()
        self.resize()

        self.set_state_main_menu()

    def resize(self):
        # get current window dimensions
        self.x, self.y = self.surface.get_size()
        if hasattr(self, "board"):
            self.board.resize(self.x, self.y)
        if hasattr(self, "main_menu"):
            self.main_menu.resize(self.x, self.y)
        if hasattr(self, "pause_menu"):
            self.pause_menu.resize(self.x, self.y)
        if hasattr(self, "game_over_menu"):
            self.game_over_menu.resize(self.x, self.y)

    def window_event_capture(self, event):
        # quit
        if event.type == pygame.locals.QUIT:
            self.set_state_quit()
            return True
        # resize
        elif event.type == pygame.locals.VIDEORESIZE:
            self.resize()
            return True
        elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_q:
                self.set_state_quit()
            return True
        else:
            return False

    def set_state_quit(self):
        if hasattr(self, "board"):
            self.board.pause()
            del self.board
        if hasattr(self, "main_menu"):
            del self.main_menu
        if hasattr(self, "pause_menu"):
            del self.pause_menu
        self.state = GameState.QUIT

    def set_state_play(self):
        if hasattr(self, "main_menu"):
            del self.main_menu
        if hasattr(self, "pause_menu"):
            del self.pause_menu
        if self.state == GameState.PAUSE:
            self.board.unpause()
        else:
            players = self.settings['players']
            player_white = players[PieceColor.WHITE](
                    PieceColor.WHITE,
                    self.settings)
            player_black = players[PieceColor.BLACK](
                    PieceColor.BLACK,
                    self.settings)

            self.board = GameBoard(
                dims=(self.x, self.y),
                coords=(0, 0),
                color=self.settings['colors']['game_board'],
                player_white=player_white,
                player_black=player_black,
                bottom_color=self.settings['initial_bottom_color'],
                settings=self.settings,
                game_over_func=self.set_state_game_over)

        self.state = GameState.PLAY

    def set_state_main_menu(self):
        if hasattr(self, "board"):
            self.board.pause()
            del self.board
        if hasattr(self, "pause_menu"):
            del self.pause_menu
        if hasattr(self, "game_over_menu"):
            del self.game_over_menu
        self.state = GameState.MAIN_MENU
        self.main_menu = MainMenu(
                (self.x, self.y),
                self.set_state_play,
                self.settings)

    def set_state_pause(self):
        self.board.pause()
        if hasattr(self, "main_menu"):
            del self.main_menu
        self.pause_menu = PauseMenu(
                (self.x, self.y),
                play_func=self.set_state_play,
                quit_func=self.set_state_main_menu,
                restarting_func=self.restart_game,
                orientation_func=self.board.spin)
        self.state = GameState.PAUSE

    def set_state_game_over(self, title, message):
        if hasattr(self, "main_menu"):
            del self.main_menu
        self.game_over_menu = GameOverMenu(
                (self.x, self.y),
                quit_func=self.set_state_main_menu,
                restarting_func=self.restart_game,
                title=title,
                message=message
                )
        self.state = GameState.GAME_OVER

    def restart_game(self):
        self.state = GameState.PLAY
        self.set_state_play()

    def play_event_capture(self, event):
        if event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_p:
                self.set_state_pause()

        self.board.event_capture(event)

    def game_loop(self):

        while self.state != GameState.QUIT:
            self.surface.fill(self.settings['colors']['clear_screen'])

            # event capture
            events = pygame.event.get()
            for event in events:
                self.window_event_capture(event)

                # event driven machine state actions
                if self.state == GameState.PLAY:
                    self.play_event_capture(event)

            # general state machine actions (like update)
            if self.state == GameState.MAIN_MENU:
                self.main_menu.update(self.surface, events)
            elif self.state == GameState.PLAY:
                self.board.draw(self.surface)
            elif self.state == GameState.PAUSE:
                self.board.draw(self.surface)
                self.pause_menu.update(self.surface, events)
            elif self.state == GameState.GAME_OVER:
                self.board.draw(self.surface)
                self.game_over_menu.update(self.surface, events)

            pygame.display.update()
            pygame.time.Clock().tick(60)


if __name__ == "__main__":
    PyChess().game_loop()
