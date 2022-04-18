#!/usr/bin/env python3
import threading
from enum import Enum
from typing import Tuple

from piece import PieceColor, PieceCode
from piece import piece_class_from_code


class GameBoardPlayer(Enum):
    WHITE = 'w'
    BLACK = 'b'


# controls the logic and board state using the FEN code
class GameBoardController():
    def __init__(self):
        # fen code attributes
        self._turn = GameBoardPlayer.WHITE
        self._turn_lock = threading.Lock()
        self.castling = 'kQKq'
        self.halfmoves = 0
        self.fullmoves = 0
        self.winner = None
        self.pieces = []
        for i in range(8):
            self.pieces.append([])
            for j in range(8):
                self.pieces[i].append(None)
        self.set_initial_fen()

    def move_piece(self, old: Tuple[int, int], new: Tuple[int, int]):
        self.pieces[new[0]][new[1]] = self.pieces[old[0]][old[1]]
        self.pieces[old[0]][old[1]] = None

    def validate(self, old_pos, new_pos):
        piece = self.pieces[old_pos[0]][old_pos[1]]
        if piece is not None:
            return piece.validate(old_pos, new_pos, self.pieces)

    def finish_turn(self):
        self._turn_lock.acquire()
        if self._turn == GameBoardPlayer.WHITE:
            self._turn = GameBoardPlayer.BLACK
        else:
            self._turn = GameBoardPlayer.WHITE
        self._turn_lock.release()

    def piece_info(self, idxs: Tuple[int, int]):
        piece = self.pieces[idxs[0]][idxs[1]]
        if piece is not None:
            return piece.type, piece.color
        else:
            return None

    def set_initial_fen(self):
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w kQKq 0 0"

    @property
    def turn(self):
        with self._turn_lock:
            return self._turn

    @turn.setter
    def turn(self, t: GameBoardPlayer):
        with self._turn_lock:
            self._turn = t

    @property
    def fen(self):
        fen = ""
        for row in self.pieces:
            empty = 0
            for piece in row:
                if piece is None:
                    empty += 1
                else:
                    if empty != 0:
                        fen += str(empty)
                    if piece.color == PieceColor.WHITE:
                        fen += piece.type.value.upper()
                    elif piece.color == PieceColor.BLACK:
                        fen += piece.type.value.lower()
            if empty != 0:
                fen += str(empty)

            fen += '/'

        # remove last '/'
        fen = fen[:-1]

        fen += " " + self.turn.value
        fen += " " + self.castling
        fen += " " + str(self.halfmoves)
        fen += " " + str(self.fullmoves)
        return fen

    @fen.setter
    def fen(self, fen_code):
        rows = fen_code.split('/')
        # separate last row placement from other attributes
        rows[-1], attrs = rows[-1].split(' ', 1)

        # piece placement
        for i, row in enumerate(rows):
            j = 0
            for c in row:
                if c.upper() in 'PNBRQK':
                    color = PieceColor.BLACK
                    if c.isupper():
                        color = PieceColor.WHITE
                    piece_class = piece_class_from_code(PieceCode(c.upper()))
                    self.pieces[i][j] = piece_class(color)
                    j += 1
                else:
                    j += int(c)

        # game attributes (turn, castling, en passant)
        attrs = attrs.split(' ')
        self.turn = GameBoardPlayer(attrs[0])
        self.castling = attrs[1]
        self.halfmoves = int(attrs[2])
        self.fullmoves = int(attrs[3])
