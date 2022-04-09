#!/usr/bin/env python3

import pygame
import pygame.locals
from enum import Enum

from game_board import GameBoard
from main_menu import MainMenu
from pause_menu import PauseMenu

CLEAR_COLOR = (22, 22, 22)


class GameState(Enum):
    MAIN_MENU = 1
    PAUSE = 2
    QUIT = 3
    PLAY = 4


class PyChess():
    def __init__(self):
        pygame.init()
        # get surface where we will draw stuff to
        self.surface = pygame.display.set_mode((400, 400), pygame.RESIZABLE)
        self.x, self.y = self.surface.get_size()
        self.resize()

        self.set_state_main_menu()

    def resize(self):
        # get current window dimensions
        self.x, self.y = self.surface.get_size()
        if hasattr(self, "board"):
            self.board.dims = (self.x, self.y)
        if hasattr(self, "main_menu"):
            self.main_menu.resize(self.x, self.y)
        if hasattr(self, "pause_menu"):
            self.pause_menu.resize(self.x, self.y)

    def window_event_capture(self, event):
        # quit
        if event.type == pygame.locals.QUIT:
            self.state = GameState.QUIT
            return True
        # resize
        elif event.type == pygame.locals.VIDEORESIZE:
            self.resize()
            return True
        elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_BACKSPACE:
                self.state = GameState.QUIT
            return True
        else:
            return False

    def set_state_play(self):
        if hasattr(self, "main_menu"):
            del self.main_menu
        if hasattr(self, "pause_menu"):
            del self.pause_menu
        self.state = GameState.PLAY
        self.board = GameBoard(
            dims=(self.x, self.y),
            coords=(0, 0),
            color=(24, 240, 128))
        self.board.set_initial_fen()

    def set_state_main_menu(self):
        if hasattr(self, "board"):
            del self.board
        if hasattr(self, "pause_menu"):
            del self.pause_menu
        self.state = GameState.MAIN_MENU
        self.main_menu = MainMenu((self.x, self.y), self.set_state_play)

    def set_state_pause(self):
        if hasattr(self, "main_menu"):
            del self.main_menu
        self.pause_menu = PauseMenu(
                (self.x, self.y),
                play_func=self.set_state_play,
                quit_func=self.set_state_main_menu)
        self.state = GameState.PAUSE

    def play_event_capture(self, event):
        if event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_p:
                self.set_state_pause()

    def game_loop(self):

        while self.state != GameState.QUIT:
            self.surface.fill(CLEAR_COLOR)

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
                self.board.update(self.surface)
                self.pause_menu.update(self.surface, events)

            pygame.display.update()


if __name__ == "__main__":
    PyChess().game_loop()
