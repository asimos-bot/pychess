import pygame
import time
import threading
import random
from abc import ABC, abstractmethod

import colors
from piece import PieceColor

BORDER_THICKNESS = 5


class Player(ABC):
    def __init__(self, color: PieceColor):
        self.color = color

    @abstractmethod
    def make_move(
            self,
            piece_info_func,
            adjust_idxs_func,
            get_valid_moves_func,
            get_non_check_moves_func):
        pass

    @abstractmethod
    def draw(
            self,
            surface,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            get_valid_moves_func):
        pass

    @abstractmethod
    def event_capture(
            self,
            event,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def unpause(self):
        pass


class RandomAI(Player):
    def make_move(
            self,
            piece_info_func,
            adjust_idxs_func,
            get_valid_moves_func):
        valid_moves = set()
        for i in range(8):
            for j in range(8):
                piece_info = piece_info_func((i, j))
                if piece_info is not None and piece_info[1] == self.color:
                    for move in get_valid_moves_func((i, j)):
                        valid_moves.add(((i, j), move))
        choosen_move = random.sample(valid_moves, 1)[0]
        return choosen_move

    def draw(
            self,
            surface,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            get_valid_moves_func):
        pass

    def event_capture(
            self,
            event,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func):
        pass

    def pause(self):
        pass

    def unpause(self):
        pass


class Human(Player):
    def __init__(self, color: PieceColor):
        super(Human, self).__init__(color)
        self._from = None
        self._to = None
        self._playing = True
        self._playing_lock = threading.Lock()

    @property
    def playing(self):
        with self._playing_lock:
            return self._playing

    @playing.setter
    def playing(self, value: bool):
        with self._playing_lock:
            self._playing = value

    def pause(self):
        self.playing = False

    def unpause(self):
        self.playing = True

    def make_move(
            self,
            piece_info_func,
            adjust_idxs_func,
            get_valid_moves_func,
            get_non_check_moves_func):
        # wait until the move is done
        while self._to is None and self.playing:
            time.sleep(0.1)

        if not self.playing:
            return None

        origin = adjust_idxs_func(self._from)
        to = adjust_idxs_func(self._to)
        self._from = None
        self._to = None
        return origin, to

    def draw(
            self,
            surface,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            get_valid_moves_func,
            get_non_check_moves_func):
        if self._from is not None:
            # highlight selected tile
            tile_idxs = self._from
            tile_rect, from_tile_surf = tile_info_func(tile_idxs)
            pygame.draw.rect(
                    from_tile_surf,
                    colors.PIECE_SELECTION,
                    (0, 0, tile_rect.w, tile_rect.w),
                    BORDER_THICKNESS,
                    border_radius=10)

            control_idxs = adjust_idxs_func(self._from)
            valid_moves = get_valid_moves_func(control_idxs)
            for valid_move in get_non_check_moves_func(control_idxs,valid_moves):
                tile_of_valid_move = adjust_idxs_func(valid_move)
                tile_rect, from_tile_surf = tile_info_func(tile_of_valid_move)
                from_tile_surf = from_tile_surf
                pygame.draw.rect(
                        from_tile_surf,
                        colors.VALID_MOVE,
                        (0, 0, tile_rect.w, tile_rect.w),
                        BORDER_THICKNESS,
                        border_radius=10
                        )

    def _get_tile_pos_from_mouse(self, pos, tile_info_func):
        for i in range(8):
            for j in range(8):
                tile_rect, _ = tile_info_func((i, j))
                if tile_rect.collidepoint(pos):
                    return i, j

    def event_capture(
            self,
            event,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func):
        if self._from is None:
            if event.type == pygame.MOUSEBUTTONDOWN:
                idxs = self._get_tile_pos_from_mouse(event.pos, tile_info_func)
                if idxs is not None:
                    control_idxs = adjust_idxs_func(idxs)
                    piece_info = piece_info_func(control_idxs)
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
