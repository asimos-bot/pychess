#!/usr/bin/env python3
import threading
from enum import Enum

from piece import PieceColor, PieceCode, SpecialMoveNotification
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
        self.castling = 'KQkq'
        self.halfmoves = 0
        self.fullmoves = 0
        self.en_passant = None
        self.winner = None
        self.pieces = []
        for i in range(8):
            self.pieces.append([])
            for j in range(8):
                self.pieces[i].append(None)
        self.set_initial_fen()

    def move_piece(self, old: (int, int), new: (int, int)):
        self.pieces[new[0]][new[1]] = self.pieces[old[0]][old[1]]
        self.pieces[old[0]][old[1]] = None
        # if there was an en_passant available, now there isn't
        notification = self.pieces[new[0]][new[1]].notify_move(new)

        # check if an en passant capture just happened
        if self.en_passant == new:
            self.pieces[old[0]][new[1]] = None

        self.en_passant = None
        if notification == SpecialMoveNotification.EN_PASSANT_AVAILABLE:
            self.en_passant = (int((old[0]+new[0])/2), new[1])
        print(self.fen)

    def get_valid_moves(self, pos: (int, int)):
        piece = self.pieces[pos[0]][pos[1]]
        if piece is not None:
            return piece.get_valid_moves(pos, self.pieces, self.en_passant)

    def finish_turn(self):
        self._turn_lock.acquire()
        if self._turn == GameBoardPlayer.WHITE:
            self._turn = GameBoardPlayer.BLACK
        else:
            self._turn = GameBoardPlayer.WHITE
        self._turn_lock.release()

    def piece_info(self, idxs: (int, int)):
        piece = self.pieces[idxs[0]][idxs[1]]
        if piece is not None:
            return piece.type, piece.color
        else:
            return None

    def set_initial_fen(self):
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"

    @property
    def turn(self):
        with self._turn_lock:
            return self._turn

    @turn.setter
    def turn(self, t: GameBoardPlayer):
        with self._turn_lock:
            self._turn = t

    def convert_to_tuple(self, idx: str):
        if len(idx) != 2:
            return None
        row = ord(idx[1].lower()) - ord('a')
        column = int(idx[0])-1
        return (row, column)

    def convert_to_idx(self, tupl):
        if tupl is None:
            return "-"
        return chr(tupl[1] + ord('a')) + str(int(tupl[0]+1))

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
        fen += " " + self.convert_to_idx(self.en_passant)
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
                    self.pieces[i][j] = piece_class(color, (i, j))
                    j += 1
                else:
                    j += int(c)

        # game attributes (turn, castling, en passant)
        attrs = attrs.split(' ')
        self.turn = GameBoardPlayer(attrs[0])
        self.castling = attrs[1]
        self.en_passant = self.convert_to_tuple(attrs[2])
        self.halfmoves = int(attrs[3])
        self.fullmoves = int(attrs[4])
