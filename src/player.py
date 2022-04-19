import pygame
import time
from abc import ABC, abstractmethod

import colors
from piece import PieceColor

BORDER_THICKNESS = 5


class Player(ABC):
    def __init__(self, color: PieceColor):
        self.color = color

    @abstractmethod
    def make_move(self, piece_info_func):
        pass

    @abstractmethod
    def draw(self, surface):
        pass

    @abstractmethod
    def event_capture(self, event, piece_info_func, tile_info_func):
        pass


class Human(Player):
    def __init__(self, color: PieceColor):
        super(Human, self).__init__(color)
        self._from = None
        self._to = None

    def make_move(self, piece_info_func):
        # wait until the move is done
        while self._to is None:
            time.sleep(0.1)

        origin = self._from
        to = self._to
        self._from = None
        self._to = None
        return origin, to

    def draw(self, surface, piece_info_func, tile_info_func):
        if self._from is not None:
            # highlight selected tile
            tile_rect, from_tile_surf = tile_info_func(
                    self._from[0],
                    self._from[1])
            pygame.draw.rect(
                    from_tile_surf,
                    colors.PIECE_SELECTION,
                    (0, 0, tile_rect.w, tile_rect.w),
                    BORDER_THICKNESS,
                    border_radius=10)

    def _get_tile_pos_from_mouse(self, pos, tile_info_func):
        for i in range(8):
            for j in range(8):
                tile_rect, _ = tile_info_func(i, j)
                if tile_rect.collidepoint(pos):
                    return i, j

    def event_capture(self, event, piece_info_func, tile_info_func):
        if self._from is None:
            if event.type == pygame.MOUSEBUTTONDOWN:
                idxs = self._get_tile_pos_from_mouse(event.pos, tile_info_func)
                if idxs is not None:
                    piece_info = piece_info_func(idxs)
                    if piece_info is None or piece_info[1] != self.color:
                        return
                    self._from = idxs
                    return
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                idxs = self._get_tile_pos_from_mouse(event.pos, tile_info_func)
                if idxs is not None:
                    if idxs == self._from:
                        self._from = None
                    else:
                        self._to = idxs
                    return
