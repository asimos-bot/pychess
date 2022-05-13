#!/usr/bin/env python3
import threading
from enum import Enum

from piece import PieceColor, PieceCode, MoveNotification
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

        # notify piece of the move, so it can update its internal state
        # and return additional information
        piece = self.pieces[old[0]][old[1]]
        notification, data = piece.notify_move(
                new,
                self.piece_info,
                self.en_passant,
                self.get_color_castlings(piece.color))

        # move piece
        self.pieces[new[0]][new[1]] = piece
        self.pieces[old[0]][old[1]] = None

        self.process_move_notification(piece, notification, data, new)

        print(self.fen)

    def process_move_notification(self, piece, notification, data, new_pos):

        self.en_passant = None
        if notification == MoveNotification.DOUBLE_START:
            # update en passant tile
            self.en_passant = data
        elif notification == MoveNotification.EN_PASSANT_DONE:
            # consume captured piece
            self.pieces[data[0]][data[1]] = None
        elif notification in [
                MoveNotification.BREAK_KING_CASTLING,
                MoveNotification.BREAK_QUEEN_CASTLING,
                MoveNotification.BREAK_CASTLING]:
            # remove partial castling
            key = notification.value
            if piece.color == PieceColor.BLACK:
                key = key.lower()
            self.castling = self.castling.replace(key, '')
            if self.castling == "":
                self.castling = "-"
        elif notification in [
                MoveNotification.QUEEN_CASTLING,
                MoveNotification.KING_CASTLING]:
            # revoke castling rights
            rook = self.pieces[data['old'][0]][data['old'][1]]
            self.pieces[data['new'][0]][data['new'][1]] = rook
            self.pieces[data['old'][0]][data['old'][1]] = None

            self.break_castling(piece.color)

        elif notification == MoveNotification.SIMPLE_CAPTURE:
            self.break_partial_castling(data, new_pos)

    def break_partial_castling(
            self,
            piece_info: (PieceCode, PieceColor),
            pos: (int, int)):

        piece_type, piece_color = piece_info
        rook_corners = {(0, 0), (0, 7), (7, 0), (7, 7)}
        if pos in rook_corners and piece_type == PieceCode.ROOK:
            key = "q"
            if pos[1] == 7:
                key = "k"
            if piece_color == PieceColor.WHITE:
                key = key.upper()
            self.castling = self.castling.replace(key, '')
            if self.castling == "":
                self.castling = "-"

    def break_castling(self, color):
        keys = ["k", "q"]
        if color == PieceColor.WHITE:
            keys = map(lambda x: x.upper(), keys)
        for key in keys:
            self.castling = self.castling.replace(key, '')
        if self.castling == "":
            self.castling = "-"

    def get_valid_moves(self, pos: (int, int)):
        piece = self.pieces[pos[0]][pos[1]]
        if piece is not None:
            return piece.get_valid_moves(
                    pos,
                    self.piece_info,
                    self.en_passant,
                    self.get_color_castlings(piece.color))

    def finish_turn(self):
        self._turn_lock.acquire()
        if self._turn == GameBoardPlayer.WHITE:
            self._turn = GameBoardPlayer.BLACK
        else:
            self.fullmoves += 1
            self._turn = GameBoardPlayer.WHITE
        self._turn_lock.release()
        self.halfmoves += 1

    def piece_info(self, idxs: (int, int)):
        piece = self.pieces[idxs[0]][idxs[1]]
        if piece is not None:
            return piece.type, piece.color
        else:
            return None

    def set_initial_fen(self):
        #self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"
        self.fen = "rnbqkb1r/ppp1p2p/5p2/8/5Pp1/2NPpNPB/PPPBQ2P/R3K2n b Qkq - 19 9"

    @property
    def turn(self):
        with self._turn_lock:
            return self._turn

    @turn.setter
    def turn(self, t: GameBoardPlayer):
        with self._turn_lock:
            self._turn = t

    def get_color_castlings(self, color: PieceColor) -> str:
        if self.castling == "-":
            return ""
        filter_func = (lambda c: c.islower())
        if color == PieceColor.WHITE:
            filter_func = (lambda c: c.isupper())
        return "".join(filter(filter_func, self.castling)).lower()

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
                        empty = 0
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

        if len(rows) != 8:
            raise Exception("Invalid number of rows for FEN string:", fen_code)

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
            if j != 8:
                raise Exception(
                        "Invalid number of pieces for row",
                        i,
                        ":",
                        row)

        # game attributes (turn, castling, en passant)
        attrs = attrs.split(' ')

        if len(attrs) != 5:
            raise Exception("Invalid number of attributes:", attrs)

        self.turn = GameBoardPlayer(attrs[0])
        self.castling = attrs[1]
        self.en_passant = self.convert_to_tuple(attrs[2])
        self.halfmoves = int(attrs[3])
        self.fullmoves = int(attrs[4])
