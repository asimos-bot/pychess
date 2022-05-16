#!/usr/bin/env python3
import threading
from enum import Enum

from matplotlib.pyplot import pie

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
        self.set_initial_fen()

    #checking if king is being attacked by an enemy piece
    def in_check(self, next_moves):
        for move in next_moves:
            piece = self.pieces[move[0]][move[1]]
            if piece is not None:
                if piece.type == PieceCode.KING:
                    return True
        return False
    
    def get_non_check_moves(self,old,valid_moves):
        piece = self.pieces[old[0]][old[1]]
        enemy_moves = []
        valid_moves_for_no_check = []
        if piece.type != PieceCode.KING:
            return valid_moves
            # king_in_range_valid_moves = self.get_king_index_and_return_valid_moves(piece,valid_moves,old)
            # if king_in_range_valid_moves is None:
            #     return valid_moves
            # else:
            #     return king_in_range_valid_moves
        for board_x in self.pieces:
            for enemy_piece in board_x:
                if enemy_piece is not None:
                    if piece.color != enemy_piece.color:
                        if piece.type == PieceCode.KING:
                            moves = self.get_valid_moves(enemy_piece.pos, is_king=1)
                            for move in moves:
                                if move not in enemy_moves:
                                    enemy_moves.append(move)    
                            
        for move in valid_moves:
            if move not in enemy_moves:
                valid_moves_for_no_check.append(move)

        return valid_moves_for_no_check
        
    def get_king_index_and_return_valid_moves(self,piece,valid_moves,old):
        directions = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(-1,-1),(-1,1),(1,-1)]
        for direction in directions:
            counter = 1
            while True:
                if (0 <= (old[0]*+direction[0]*counter) <= 7 and 0 <= (old[1]+direction[1]*counter) <= 7):
                    coord = (old[0]*+direction[0]*counter,old[1]+direction[1]*counter)
                    print(coord)
                    r_piece = self.pieces[old[0]*+direction[0]*counter][old[1]+direction[1]*counter]
                    if r_piece is not None:
                        if r_piece.type == PieceCode.KING and r_piece.color == piece.color:
                            return self.get_valid_moves_if_king_is_in_range(piece,direction,valid_moves,old)
                    counter +=1
                else:
                    break
        
        return None

    def get_valid_moves_if_king_is_in_range(self,piece,direction,valid_moves,old):
        enemy_possible_direction = (direction[0]*-1,direction[1]*-1)
        possible_moves = []
        counter = 1
        if(enemy_possible_direction[0] == 0 or enemy_possible_direction[1] == 0):
            while True:
                if (0 <= (old[0]+enemy_possible_direction[0]*counter) <= 7 and 0 <= (old[1]+enemy_possible_direction[1]*counter) <= 7):
                    r_piece = self.pieces[old[0]+enemy_possible_direction[0]*counter][old[1]+enemy_possible_direction[1]*counter]
                    if (r_piece is not None and r_piece.color != piece.color):
                        if(r_piece.type != PieceCode.ROOK or r_piece.type != PieceCode.QUEEN):
                            return None
                        elif((r_piece.type == PieceCode.ROOK or r_piece.type == PieceCode.QUEEN) and (piece.type == PieceCode.ROOK or piece.type == PieceCode.QUEEN)):
                            possible_moves.append((old[0]+enemy_possible_direction[0]*counter,old[1]+enemy_possible_direction[1]*counter))
                            return possible_moves        
                    else:
                        if(piece.type == PieceCode.ROOK or piece.type == PieceCode.QUEEN):
                            possible_moves.append((old[0]+enemy_possible_direction[0]*counter,old[1]+enemy_possible_direction[1]*counter))
                    counter += 1 
        else:
            while True:
                if (0 <= (old[0]+enemy_possible_direction[0]*counter) <= 7 and 0 <= (old[1]+enemy_possible_direction[1]*counter) <= 7):
                    r_piece = self.pieces[old[0]+enemy_possible_direction[0]*counter][old[1]+enemy_possible_direction[1]*counter]
                    if (r_piece is not None and r_piece.color != piece.color):
                        if(r_piece.type != PieceCode.BISHOP or r_piece.type != PieceCode.QUEEN):
                            return None
                        elif((r_piece.type == PieceCode.BISHOP or r_piece.type == PieceCode.QUEEN) and (piece.type == PieceCode.BISHOP or piece.type == PieceCode.QUEEN)):
                            possible_moves.append((old[0]+enemy_possible_direction[0]*counter,old[1]+enemy_possible_direction[1]*counter))
                            return possible_moves  
                    else:
                        if(piece.type == PieceCode.BISHOP or piece.type == PieceCode.QUEEN):
                            possible_moves.append((old[0]+enemy_possible_direction[0]*counter,old[1]+enemy_possible_direction[1]*counter))
                    counter += 1 


                    
        


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

    def get_valid_moves(self, pos: (int, int), is_king=0):
        piece = self.pieces[pos[0]][pos[1]]
        if piece is not None:
            return piece.get_valid_moves(
                    pos,
                    self.piece_info,
                    self.en_passant,
                    self.get_color_castlings(piece.color)
                    ,is_king)

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
        self.fen = "rnbqkbnr/8/8/8/8/8/8/RNBQKBNR w KQkq - 0 0"

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
        column = ord(idx[0].lower()) - ord('a')
        row = 8-int(idx[1])
        return (row, column)

    def convert_to_idx(self, tupl):
        if tupl is None:
            return "-"
        return chr(tupl[1] + ord('a')) + str(8-int(tupl[0]))

    def clear_board(self):
        self.pieces = []
        for i in range(8):
            self.pieces.append([])
            for j in range(8):
                self.pieces[i].append(None)

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
        self.clear_board()
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
