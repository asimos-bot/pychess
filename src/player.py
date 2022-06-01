import pygame
import time
import threading
import random
from abc import ABC, abstractmethod

from piece import PieceColor, PieceCode

BORDER_THICKNESS = 5


class Player(ABC):
    def __init__(self, color: PieceColor, settings: dict()):
        self.color = color
        self.settings = settings
        self._playing = True
        self._playing_lock = threading.Lock()

    @abstractmethod
    def make_move(
            self,
            piece_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func) -> ((int, int), (int, int), PieceCode):
        pass

    @abstractmethod
    def draw(
            self,
            surface,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func):
        pass

    @abstractmethod
    def event_capture(
            self,
            event,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            is_promotion_valid_func):
        pass

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


class RandomAI(Player):
    def __init__(self, color: PieceColor, settings: dict()):
        super(RandomAI, self).__init__(color, settings)

    def make_move(
            self,
            piece_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func):

        if not self.playing:
            return None

        legal_moves = set()
        for i in range(8):
            for j in range(8):
                piece_info = piece_info_func((i, j))
                if piece_info is not None and piece_info[1] == self.color:
                    for move in get_legal_moves_func((i, j)):
                        legal_moves.add(((i, j), move))
        choosen_move = random.sample(legal_moves, 1)[0]
        random_promotion = [
                PieceCode.QUEEN,
                PieceCode.KNIGHT,
                PieceCode.BISHOP,
                PieceCode.ROOK][random.randint(0, 3)]
        choosen_move = (choosen_move[0], choosen_move[1], random_promotion)
        return choosen_move

    def draw(
            self,
            surface,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func):
        pass

    def event_capture(
            self,
            event,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            is_promotion_valid_func):
        pass


class Human(Player):
    def __init__(self, color: PieceColor, settings: dict()):
        super(Human, self).__init__(color, settings)
        self._from = None
        self._to = None
        self.wait_promotion = False
        self.choosen_promotion = None

    def make_move(
            self,
            piece_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func):
        # wait until the move is done
        while (self._to is None or self.wait_promotion) and self.playing:
            time.sleep(0.1)

        if not self.playing:
            return None

        # convert graphical position to controller position
        origin = adjust_idxs_func(self._from)
        to = adjust_idxs_func(self._to)

        # handle promotion
        promotion = None

        self._from = None
        self._to = None
        self.choosen_promotion = None
        return origin, to, promotion

    def draw(
            self,
            surface,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func):
        if self._from is not None:
            # highlight selected tile
            tile_idxs = self._from
            tile_rect, from_tile_surf = tile_info_func(tile_idxs)
            pygame.draw.rect(
                    from_tile_surf,
                    self.settings['colors']['piece_selection'],
                    (0, 0, tile_rect.w, tile_rect.w),
                    BORDER_THICKNESS,
                    border_radius=10)

            control_idxs = adjust_idxs_func(self._from)
            for valid_move in get_legal_moves_func(control_idxs):
                tile_of_valid_move = adjust_idxs_func(valid_move)
                tile_rect, from_tile_surf = tile_info_func(tile_of_valid_move)
                from_tile_surf = from_tile_surf
                pygame.draw.rect(
                        from_tile_surf,
                        self.settings['colors']['valid_move'],
                        (0, 0, tile_rect.w, tile_rect.w),
                        BORDER_THICKNESS,
                        border_radius=10
                        )
            if self.wait_promotion:
                if self.color == PieceCode.WHITE:
                    pass

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
            adjust_idxs_func,
            is_promotion_valid_func):
        idxs = None
        control_idxs = None
        if event.type == pygame.MOUSEBUTTONDOWN:
            idxs = self._get_tile_pos_from_mouse(event.pos, tile_info_func)
            control_idxs = adjust_idxs_func(idxs)
        if self._from is None:
            if idxs is not None:
                piece_info = piece_info_func(control_idxs)
                if piece_info is None or piece_info[1] != self.color:
                    return
                self._from = idxs
                return
        elif self._to is None:
            if idxs is not None:
                if idxs == self._from:
                    self._from = None
                else:
                    self._to = idxs
                    # check if we must wait for promotion
                    piece_info = piece_info_func(self._from)
                    piece_type, piece_color = piece_info
                    self.wait_promotion = is_promotion_valid_func(
                            control_idxs,
                            piece_type,
                            piece_color,
                            PieceCode.QUEEN)  # random valid promotion
        elif self.wait_promotion:
            if idxs is not None and idxs != self._from:
                self._to = None
                self._from = None
