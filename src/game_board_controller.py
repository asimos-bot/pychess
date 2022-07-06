#!/usr/bin/env python3
import threading

from piece import Piece, PieceColor, PieceCode, MoveNotification
from piece import piece_class_from_code


# controls the logic and board state using the FEN code
class GameBoardController():
    def __init__(self):
        # fen code attributes
        self._turn: PieceColor = PieceColor.WHITE
        self._turn_lock = threading.Lock()
        self.castling = 'KQkq'
        self.halfmoves = 0
        self.fullmoves = 0
        self.en_passant = None
        self.winner = None
        self.pieces = []

        self.rule_50_moves_draw = 100
        self.claim_draw = False
        self.threefold_draw = False
        self.insufficent_cmr_draw = False
        self.stalemate_draw = False
        self.white_threefold = []
        self.white_last_moved_piece = None
        self.white_before_last_moved_piece = None
        self.white_moved_times = 1
        self.black_threefold = []
        self.black_last_moved_piece = None
        self.black_before_last_moved_piece = None
        self.black_moved_times = 1
        self.black_last_old_and_new = None
        self.white_last_old_and_new = None

        self.pieces_by_color = {
                PieceColor.WHITE: set(),
                PieceColor.BLACK: set()
                }

        self.attackable_tiles_from = {
                PieceColor.WHITE: set(),
                PieceColor.BLACK: set()
                }
        self.set_initial_fen()

    def copy(self):
        controller = GameBoardController()
        controller.fen = self.fen
        return controller

    def move_piece(
            self,
            old: (int, int),
            new: (int, int),
            promotion: PieceCode):

        # notify piece of the move, so it can update its internal state
        # and return additional information
        piece = self.pieces[old[0]][old[1]]
        notification, data = piece.notify_move(
                new,
                self.piece_info,
                self.en_passant,
                self.get_color_castlings(piece.color))

        # move piece
        # remove piece from pieces_by_color set
        if self.pieces[new[0]][new[1]] is not None:
            enemy_color = self.opposite_color(piece.color)
            self.pieces_by_color[enemy_color].remove(new)

        self.pieces[new[0]][new[1]] = piece
        self.pieces[old[0]][old[1]] = None

        self.pieces_by_color[piece.color].remove(old)
        self.pieces_by_color[piece.color].add(new)

        self.process_move_notification(piece, notification, data, new)

        # handle promotion
        self.promote(piece, promotion)

        self.update_pseudo_legal_moves()

    def is_promotion_valid(
            self,
            pos: (int, int),
            piece_type: PieceCode,
            piece_color: PieceColor,
            promotion: PieceCode):
        # is promotion a valid promotion piece?
        if promotion not in [
                PieceCode.QUEEN,
                PieceCode.KNIGHT,
                PieceCode.ROOK,
                PieceCode.BISHOP]:
            return False
        # is piece a pawn?
        if piece_type != PieceCode.PAWN:
            return False
        # is pawn at the last tile opposite to its color starting side?
        white_promotion = pos[0] == 7 and piece_color == PieceColor.BLACK
        black_promotion = pos[0] == 0 and piece_color == PieceColor.WHITE
        if not white_promotion and not black_promotion:
            return False
        # if you get here, promotion is valid!
        return True

    def promote(self, piece: Piece, promotion: PieceCode):
        if self.is_promotion_valid(
                piece.pos,
                piece.type,
                piece.color,
                promotion):
            new_piece = piece_class_from_code(promotion)(
                    piece.color,
                    piece.pos)
            self.pieces[piece.pos[0]][piece.pos[1]] = new_piece

    def fifty_move_rule(self, old: (int, int), new: (int, int)):

        piece = self.pieces[old[0]][old[1]]
        is_piece = self.pieces[new[0]][new[1]] is not None
        is_pawn = piece.type == PieceCode.PAWN
        if is_pawn or is_piece:
            self.rule_50_moves_draw = 100
            self.claim_draw = False
            return
        self.rule_50_moves_draw -= 1
        if self.rule_50_moves_draw <= 0:
            self.claim_draw = True

    def insufficient_checkmate_material_rule(self):
        white_positions = self.pieces_by_color[PieceColor.WHITE]
        black_positions = self.pieces_by_color[PieceColor.BLACK]
        black_knight_count = 0
        white_knight_count = 0
        if ((len(white_positions) == 2 and len(black_positions) == 2) or 
        (len(white_positions) == 3 and len(black_positions) == 1) or
        (len(white_positions) == 1 and len(black_positions) == 3) or
        (len(white_positions) == 2 and len(black_positions) == 1) or
        (len(white_positions) == 1 and len(black_positions) == 2)):
            white_pieces = []
            black_pieces = []
            is_white_in_dark_slots = False
            is_black_in_dark_slots = False
            dark_slots = [(0, 0), (0, 2), (0, 4), (0, 6),
                          (1, 1), (1, 3), (1, 5), (1, 7),
                          (2, 0), (2, 2), (2, 4), (2, 6),
                          (3, 1), (3, 3), (3, 5), (3, 7),
                          (4, 0), (4, 2), (4, 4), (4, 6),
                          (5, 1), (5, 3), (5, 5), (5, 7),
                          (6, 0), (6, 2), (6, 4), (6, 6),
                          (7, 1), (7, 3), (7, 5), (7, 7)]
            for position in white_positions:
                white_pieces.append(self.pieces[position[0]][position[1]].type)
                if(self.pieces[position[0]][position[1]].type == PieceCode.KNIGHT):
                    white_knight_count += 1
                if(self.pieces[position[0]][position[1]].type == PieceCode.BISHOP and position in dark_slots):
                    is_white_in_dark_slots = True
            for position in black_positions:
                black_pieces.append(self.pieces[position[0]][position[1]].type)
                if(self.pieces[position[0]][position[1]].type == PieceCode.KNIGHT):
                    black_knight_count += 1
                if(self.pieces[position[0]][position[1]].type == PieceCode.BISHOP and position in dark_slots):
                    is_black_in_dark_slots = True
            if ((PieceCode.KING in white_pieces and PieceCode.BISHOP in white_pieces and PieceCode.KING in black_pieces and len(black_positions) == 1 and len(white_positions) == 2) or
            (PieceCode.KING in black_pieces and PieceCode.BISHOP in black_pieces and PieceCode.KING in white_pieces and len(white_positions) == 1 and len(black_positions) == 2) or
            (PieceCode.KING in white_pieces and PieceCode.KNIGHT in white_pieces and PieceCode.KING in black_pieces and len(black_positions) == 1 and len(white_positions) == 2) or
            (PieceCode.KING in black_pieces and PieceCode.KNIGHT in black_pieces and PieceCode.KING in white_pieces and len(white_positions) == 1 and len(black_positions) == 2) or
            (PieceCode.KING in white_pieces and PieceCode.KNIGHT in white_pieces and PieceCode.KING in black_pieces and len(black_positions) == 1 and len(white_knight_count) == 2) or
            (PieceCode.KING in black_pieces and PieceCode.KNIGHT in black_pieces and PieceCode.KING in white_pieces and len(white_positions) == 1 and len(black_knight_count) == 2) or
            (PieceCode.KING in white_pieces and len(white_positions) == 1 and PieceCode.KING in black_pieces and len(black_positions) == 1) or
            (is_white_in_dark_slots == is_black_in_dark_slots and PieceCode.BISHOP in black_pieces and PieceCode.BISHOP in white_pieces and len(white_positions) == 2 and len(black_positions) == 2)):
                self.insufficent_cmr_draw = True

    def threefold_repetition_rule(self, old: (int,int), new:(int, int)):
        piece = self.pieces[new[0]][new[1]]
        if(self._turn == PieceColor.WHITE):

            self.white_before_last_moved_piece = self.white_last_moved_piece
            self.white_last_moved_piece = piece
            if self.white_before_last_moved_piece is None:
                self.white_last_old_and_new = old,new
            else:
                if(self.white_before_last_moved_piece.type == piece.type and self.white_last_old_and_new[0] == new and self.white_last_old_and_new[1] == old):
                    self.white_moved_times += 1
                else:
                    self.white_moved_times = 1
            self.white_last_old_and_new = old,new
            self.white_threefold.append(new)
            if len(self.white_threefold) >= 5 and self.white_moved_times >= 5:
                if((self.white_threefold[0] == self.white_threefold[2] and self.white_threefold[2] == self.white_threefold[4]) and 
                (self.white_threefold[3] == self.white_threefold[1])):
                    self.threefold_draw = True
                    self.white_threefold.pop(0)
                else:
                    self.threefold_draw = False
                    self.white_threefold.pop(0)
            elif len(self.white_threefold) >= 5:
                self.white_threefold.pop(0)
                self.threefold_draw = False
        else:
            self.black_before_last_moved_piece = self.black_last_moved_piece
            self.black_last_moved_piece = piece

            if self.black_before_last_moved_piece is None:
                self.black_last_old_and_new = old, new
            else:
                if(self.black_before_last_moved_piece.type == piece.type and self.black_last_old_and_new[0] == new and self.black_last_old_and_new[1] == old):
                    self.black_moved_times += 1
                else:
                    self.black_moved_times = 1
            self.black_last_old_and_new = old, new
            self.black_threefold.append(new)
            if len(self.black_threefold) >= 5 and self.black_moved_times >= 5:

                if((self.black_threefold[0] == self.black_threefold[2] and self.black_threefold[2] == self.black_threefold[4]) and 
                (self.black_threefold[3] == self.black_threefold[1])):
                    self.threefold_draw = True
                    self.black_threefold.pop(0)
                else:
                    self.threefold_draw = False
                    self.black_threefold.pop(0)
            elif len(self.black_threefold) >= 5:
                self.black_threefold.pop(0)
                self.threefold_draw = False

    def stalemate_rule(self):
        if self._turn == PieceColor.WHITE:
            positions = self.pieces_by_color[PieceColor.WHITE]
        else:
            positions = self.pieces_by_color[PieceColor.BLACK]
        for position in positions:
            valid_moves = self.get_legal_moves(position)
            if len(valid_moves) > 0:
                return False
        self.stalemate_draw = True
        return True

    def is_check_valid(self, new: (int, int)):

        piece = self.pieces[new[0]][new[1]]
        moves = piece.get_pseudo_legal_moves()
        for move in moves:
            enemy_piece = self.pieces[move[0]][move[1]]
            if enemy_piece is not None:
                is_king = enemy_piece.type == PieceCode.KING
                is_enemy = enemy_piece.color != piece.color
                if is_king and is_enemy:
                    return True
        return False

    def is_checkmate_valid(self, new: (int, int)):

        piece = self.pieces[new[0]][new[1]]
        for pos in self.pieces_by_color[self.opposite_color(piece.color)]:
            enemy_piece = self.pieces[pos[0]][pos[1]]
            if len(self.get_legal_moves(enemy_piece.pos)) >= 1:
                return False
        return True

    def update_pseudo_legal_moves(self):
        self.attackable_tiles_from = {
                PieceColor.WHITE: set(),
                PieceColor.BLACK: set()
                }
        for color in PieceColor:
            for piece_idx in self.pieces_by_color[color]:
                piece = self.pieces[piece_idx[0]][piece_idx[1]]
                piece.update_pseudo_legal_moves(
                    self.piece_info,
                    self.en_passant,
                    self.get_color_castlings(piece.color))

                for attack_tile in piece.get_pseudo_legal_moves():
                    piece_type, _ = self.piece_info(piece_idx)
                    is_pawn = piece_type == PieceCode.PAWN
                    forward_attack = attack_tile[1] == piece_idx[1]
                    if is_pawn and forward_attack:
                        continue
                    self.attackable_tiles_from[color].add(attack_tile)

        # get both kings and ask them gently to make sure if castling is
        # seen as possible in this turn even though there are attackable_tiles
        # in the way
        for color in PieceColor:
            for piece_idx in self.pieces_by_color[color]:
                piece = self.pieces[piece_idx[0]][piece_idx[1]]
                piece_type, piece_color = self.piece_info(piece_idx)
                if piece_type == PieceCode.KING:
                    enemy_color = self.opposite_color(color)
                    piece.update_castling(
                            self.piece_info,
                            self.get_color_castlings(piece_color),
                            self.attackable_tiles_from[enemy_color])

    def process_move_notification(self, piece, notification, data, new_pos):

        self.en_passant = None
        if notification == MoveNotification.DOUBLE_START:
            # update en passant tile
            self.en_passant = data
        elif notification == MoveNotification.EN_PASSANT_DONE:
            # consume captured piece
            _, color = self.piece_info(data)
            self.pieces_by_color[color].remove(data)
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
            _, rook_color = self.piece_info(data['old'])
            self.pieces[data['new'][0]][data['new'][1]] = rook
            self.pieces[data['old'][0]][data['old'][1]] = None
            self.pieces_by_color[rook_color].remove(data['old'])
            self.pieces_by_color[rook_color].add(data['new'])

            self.break_castling(piece.color)

            self.pieces[data['new'][0]][data['new'][1]].pos = data['new']

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

    def get_legal_moves(self, pos: (int, int)) -> {(int, int)}:

        piece_info = self.piece_info(pos)
        if piece_info is None:
            return set()
        piece_type, piece_color = piece_info
        piece = self.pieces[pos[0]][pos[1]]
        if piece.legal_moves is not None:
            return piece.legal_moves
        legal_moves = set()
        # every possible pseudo-legal move you can make from this piece
        for move in self.get_pseudo_legal_moves(pos):
            for promotion in "QN":
                # check if we should skip the first promotion
                if promotion == "Q":
                    # if this piece is not a pawn, not reason to iterate twice
                    if piece_type != PieceCode.PAWN:
                        continue
                    # if this piece is a pawn, not reason to go over promotion
                    # if not reaching edge of board
                    if piece_type == PieceCode.PAWN and ((move[1] != 7 and piece_color == PieceColor.WHITE) or (move[1] != 0 and piece_color == PieceColor.BLACK)):
                        continue
                promotion = PieceCode(promotion)
                # create a new controller for each move
                tmp_board: GameBoardController = self.copy()
                # make the move in this temporary controller
                tmp_board.move_piece(pos, move, promotion)
                tmp_board.finish_turn()
                # iterate over every possible enemy move in this temporary
                # controller, and add this move if no enemy move can kill
                # our king
                enemy_color = self.opposite_color(piece_color)
                enemy_attack_tiles = tmp_board.attackable_tiles_from[enemy_color]
                legal_move = True
                for enemy_attack_tile in enemy_attack_tiles:
                    attack_info = tmp_board.piece_info(enemy_attack_tile)
                    if attack_info == (PieceCode.KING, piece_color):
                        legal_move = False
                del tmp_board
                if legal_move:
                    legal_moves.add(move)

        piece.legal_moves = legal_moves
        return legal_moves

    def get_pseudo_legal_moves(self, pos: (int, int)):
        piece = self.pieces[pos[0]][pos[1]]
        if piece is not None:
            return piece.get_pseudo_legal_moves()

    def finish_turn(self):
        self._turn_lock.acquire()
        if self._turn == PieceColor.WHITE:
            self._turn = PieceColor.BLACK
        else:
            self.fullmoves += 1
            self._turn = PieceColor.WHITE
        self._turn_lock.release()
        self.halfmoves += 1

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
    def turn(self, t: PieceColor):
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

        self.pieces_by_color = {
                PieceColor.WHITE: set(),
                PieceColor.BLACK: set()
                }

        self.attackable_tiles_from = {
                PieceColor.BLACK: set(),
                PieceColor.WHITE: set()
                }

    @classmethod
    def opposite_color(cls, color: PieceColor):
        if color == PieceColor.WHITE:
            return PieceColor.BLACK
        return PieceColor.WHITE

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
                    color: PieceColor = PieceColor.BLACK
                    if c.isupper():
                        color = PieceColor.WHITE
                    piece_class = piece_class_from_code(PieceCode(c.upper()))
                    piece = piece_class(color, (i, j))
                    self.pieces[i][j] = piece
                    self.pieces_by_color[color].add(piece.pos)
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

        self.turn = PieceColor(attrs[0])
        self.castling = attrs[1]
        self.en_passant = self.convert_to_tuple(attrs[2])
        self.halfmoves = int(attrs[3])
        self.fullmoves = int(attrs[4])

        self.update_pseudo_legal_moves()
