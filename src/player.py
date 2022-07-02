import pygame
import time
import threading
from abc import ABC, abstractmethod

from piece import PieceColor, PieceCode, PieceDrawer

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
            is_promotion_valid_func,
            fen_code) -> ((int, int), (int, int), PieceCode):
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


class Human(Player):
    def __init__(self, color: PieceColor, settings: dict()):
        super(Human, self).__init__(color, settings)
        self._from = None
        self._to = None
        self.wait_promotion = False
        self.choosen_promotion = None
        self.op_lock = threading.Lock()

    def make_move(
            self,
            piece_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func,
            fen_code):
        # wait until the move is done
        while (self._to is None or self.wait_promotion) and self.playing:
            time.sleep(0.1)

        if not self.playing:
            return None

        self.op_lock.acquire()
        # convert graphical position to controller position
        origin = adjust_idxs_func(self._from)
        to = adjust_idxs_func(self._to)

        # handle promotion
        promotion = self.choosen_promotion

        self._from = None
        self._to = None
        self.choosen_promotion = None

        self.op_lock.release()
        return origin, to, promotion

    def draw(
            self,
            surface,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            get_legal_moves_func,
            is_promotion_valid_func):
        self.op_lock.acquire()
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
                pygame.draw.rect(
                        from_tile_surf,
                        self.settings['colors']['valid_move'],
                        (0, 0, tile_rect.w, tile_rect.w),
                        BORDER_THICKNESS,
                        border_radius=10
                        )
            if self.wait_promotion:
                piece_type, piece_color = piece_info_func(control_idxs)
                opposite = adjust_idxs_func((0, 0)) != (0, 0)
                row = [0, 9][piece_color == PieceColor.BLACK or opposite]
                direction = [1, -1][self._to[1] > 4]

                for i, piece_type in enumerate([
                        PieceCode.QUEEN,
                        PieceCode.KNIGHT,
                        PieceCode.ROOK,
                        PieceCode.BISHOP]):
                    pos = (row, self._to[1]+direction*i)
                    tile_rect, tile_surf = tile_info_func(pos, False)
                    PieceDrawer.draw(tile_surf, piece_type, piece_color, pos)
        self.op_lock.release()

    def _get_tile_pos_from_mouse(self, pos, tile_info_func, convert=True):
        n = [10, 8][convert]
        for i in range(n):
            for j in range(n):
                tile_rect, _ = tile_info_func((i, j), convert)
                if tile_rect.collidepoint(pos):
                    return i, j

    def event_capture(
            self,
            event,
            piece_info_func,
            tile_info_func,
            adjust_idxs_func,
            is_promotion_valid_func):
        self.op_lock.acquire()
        idxs = None
        control_idxs = None
        if event.type == pygame.MOUSEBUTTONDOWN:
            idxs = self._get_tile_pos_from_mouse(event.pos, tile_info_func)
            if idxs is not None:
                control_idxs = adjust_idxs_func(idxs)
        if self._from is None:
            if idxs is not None:
                piece_info = piece_info_func(control_idxs)
                if piece_info is not None and piece_info[1] == self.color:
                    self._from = idxs
        elif self._to is None:
            if idxs is not None:
                if idxs == self._from:
                    self._from = None
                else:
                    self._to = idxs
                    # check if we must wait for promotion
                    piece_info = piece_info_func(self._from)
                    if piece_info is not None:
                        piece_type, piece_color = piece_info
                        self.wait_promotion = is_promotion_valid_func(
                                control_idxs,
                                piece_type,
                                piece_color,
                                PieceCode.QUEEN)  # random valid promotion
        elif self.wait_promotion and event.type == pygame.MOUSEBUTTONDOWN:
            from_control_idxs = adjust_idxs_func(self._from)
            piece_type, piece_color = piece_info_func(from_control_idxs)
            opposite = adjust_idxs_func((0, 0)) != (0, 0)
            row = [0, 9][piece_color == PieceColor.BLACK or opposite]
            direction = [1, -1][self._to[1] > 4]
            global_idxs = self._get_tile_pos_from_mouse(
                    event.pos,
                    tile_info_func,
                    False)

            for i, piece_type in enumerate([
                    PieceCode.QUEEN,
                    PieceCode.KNIGHT,
                    PieceCode.ROOK,
                    PieceCode.BISHOP]):
                pos = (row, self._to[1]+direction*i)
                if global_idxs == pos:
                    self.wait_promotion = False
                    self.choosen_promotion = piece_type
            if self.wait_promotion and idxs != self._to:
                self._to = None
                self.wait_promotion = False
        self.op_lock.release()
