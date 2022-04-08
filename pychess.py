#!/usr/bin/env python3

import pygame
import pygame.locals
from enum import Enum

from game_board import GameBoard


class GameState(Enum):
    MAIN_MENU = 1
    PAUSE = 2
    QUIT = 3


class PyChess():
    def __init__(self):
        pygame.init()
        # get surface where we will draw stuff to
        self.surface = pygame.display.set_mode((400, 400), pygame.RESIZABLE)
        self.x, self.y = self.surface.get_size()
        self.state: GameState = GameState.MAIN_MENU

        self.board = GameBoard(
            dims=(self.x, self.y),
            coords=(0, 0),
            color=(24, 240, 128))

        self.resize_update()

    def resize_update(self):
        # get current window dimensions
        self.x, self.y = self.surface.get_size()
        self.board.dims = (self.x, self.y)
        print(self.x, self.y)

    def game_loop(self):

        while self.state != GameState.QUIT:
            # event capture
            for event in pygame.event.get():
                # quit
                if event.type == pygame.locals.QUIT:
                    self.state = GameState.QUIT
                # resize
                elif event.type == pygame.locals.VIDEORESIZE:
                    self.resize_update()
                elif event.type == pygame.locals.KEYDOWN:
                    if event.key == pygame.locals.K_BACKSPACE:
                        self.state = GameState.QUIT

            self.board.draw(self.surface)
            pygame.display.flip()


if __name__ == "__main__":
    PyChess().game_loop()
