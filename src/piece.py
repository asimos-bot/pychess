import pygame
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path


class PieceColor(Enum):
    WHITE = 'w'
    BLACK = 'b'


class PieceCode(Enum):
    KING = 'K'
    QUEEN = 'Q'
    KNIGHT = 'N'
    BISHOP = 'B'
    PAWN = 'P'
    ROOK = 'R'


class MoveNotification(Enum):
    SIMPLE_MOVE = 1
    SIMPLE_CAPTURE = 2
    DOUBLE_START = 3
    EN_PASSANT_DONE = 4
    QUEEN_CASTLING = 'q'
    KING_CASTLING = 'k'
    BREAK_QUEEN_CASTLING = 'Q'
    BREAK_KING_CASTLING = 'K'
    BREAK_CASTLING = 'KQ'


class PieceDrawer:

    @classmethod
    def load_images(cls):
        assets_folder = Path(__file__).parent.parent.joinpath("assets")
        imgs = dict()
        for color in PieceColor:
            imgs[color] = dict()
            for piece_code in PieceCode:
                filename = color.name.lower()
                filename += "_"
                filename += piece_code.name.lower()
                filename += ".png"
                filepath = assets_folder.joinpath(filename)
                img = pygame.image.load(filepath).convert_alpha()
                imgs[color][piece_code] = {
                        'filepath': filepath,
                        'img': img
                    }
        cls.imgs = imgs

    @classmethod
    def resize(cls, dims):
        cls.load_images()
        dims = (int(dims[0]), int(dims[1]))
        for color in PieceColor:
            for piece_code in PieceCode:
                img_info = cls.imgs[color][piece_code]
                filepath = img_info['filepath']
                img_info['img'] = pygame.image.load(filepath).convert_alpha()
                img_info['img'] = pygame.transform.scale(img_info['img'], dims)

    @classmethod
    def draw(
            cls,
            surface,
            piece_code: PieceCode,
            color: PieceColor,
            coords=(0, 0)):
        surface.blit(cls.imgs[color][piece_code]['img'], coords)


class Piece(ABC):

    def __init__(self, color: PieceColor, pos: (int, int)):
        self.color = color
        self.pos = pos
        self.pseudo_legal_moves = set()

    @property
    @abstractmethod
    def type(self) -> PieceCode:
        pass

    @abstractmethod
    def update_pseudo_legal_moves(
            self,
            pos: (int, int),
            piece_info_func,
            en_passant,
            castling):
        pass

    def get_pseudo_legal_moves(self):
        return self.pseudo_legal_moves

    # called before the move actually happens
    # used to update internal piece state and
    # return additional information about this move
    def notify_move(
            self,
            pos: (int, int),
            piece_info_func,
            en_passant,
            castling) -> (MoveNotification, any):
        self.pos = pos
        piece = piece_info_func(self.pos)
        if piece is not None:
            return (MoveNotification.SIMPLE_CAPTURE, piece)
        else:
            return (MoveNotification.SIMPLE_MOVE, pos)


class Pawn(Piece):

    def __init__(self, color: PieceColor, pos: (int, int)):
        super(Pawn, self).__init__(color, pos)
        self.direction = [1, -1][self.color == PieceColor.WHITE]
        white_first_move = PieceColor.WHITE == self.color and pos[0] == 6
        black_first_move = PieceColor.BLACK == self.color and pos[0] == 1
        self.first_move = white_first_move or black_first_move

    @property
    def type(self):
        return PieceCode.PAWN

    def notify_move(
            self,
            pos: (int, int),
            piece_info_func,
            en_passant,
            castling) -> (MoveNotification, any):
        # this can be a simple_move, a double start or an en passant
        old_pos = self.pos
        # simple move
        notify = super(Pawn, self).notify_move(
                pos,
                piece_info_func,
                en_passant,
                castling)
        # double start
        if self.first_move and abs(old_pos[0] - pos[0]) == 2:
            en_passant = (old_pos[0] + self.direction, self.pos[1])
            notify = (MoveNotification.DOUBLE_START, en_passant)
        # en passant
        elif notify[0] == MoveNotification.SIMPLE_MOVE:
            if pos == en_passant:
                captured = (old_pos[0], pos[1])
                notify = (MoveNotification.EN_PASSANT_DONE, captured)

        self.first_move = False
        return notify

    def update_pseudo_legal_moves(
            self,
            piece_info_func,
            en_passant,
            castling):
        pseudo_legal_moves = set()

        def add_if_pseudo_legal(_set, pos):
            i, j = pos
            if 0 <= i <= 7 and 0 <= j <= 7:
                piece = piece_info_func
                piece_can_be_replaced = piece is None or piece[1] != self.color
                if 0 <= i <= 7 and 0 <= j <= 7 and piece_can_be_replaced:
                    _set.add(pos)

        # forward
        forward = (self.pos[0] + self.direction, self.pos[1])
        forward_available = False
        if 0 <= forward[0] <= 7 and piece_info_func(forward) is None:
            pseudo_legal_moves.add(forward)
            forward_available = True

        # double start check
        if self.first_move:
            double_forward = (self.pos[0] + 2 * self.direction, self.pos[1])
            inside_board = 0 <= double_forward[0] <= 7
            double_forward_available = piece_info_func(double_forward) is None
            if inside_board and double_forward_available and forward_available:
                pseudo_legal_moves.add(double_forward)

        # there is an en passant
        if en_passant is not None:
            # row position tells it is possible
            if en_passant[0] == self.pos[0] + self.direction:
                # column position confirms it is possible
                if abs(en_passant[1] - self.pos[1]) == 1:
                    pseudo_legal_moves.add(en_passant)

        # eat diagonals
        diagonal_1 = (self.pos[0] + self.direction, self.pos[1] + 1)
        diagonal_2 = (self.pos[0] + self.direction, self.pos[1] - 1)
        diagonals = (diagonal_1, diagonal_2)

        # check if pieces from the other color are in a frontal
        # diagonal, ready to be captured
        for diagonal in diagonals:
            if 0 <= diagonal[0] <= 7 and 0 <= diagonal[1] <= 7:
                piece = piece_info_func(diagonal)
                if piece is not None and piece[1] != self.color:
                    pseudo_legal_moves.add(diagonal)

        self.pseudo_legal_moves = pseudo_legal_moves


class Knight(Piece):

    @property
    def type(self):
        return PieceCode.KNIGHT

    def update_pseudo_legal_moves(
            self,
            piece_info_func,
            en_passant,
            castling):
        pseudo_legal_moves = set()
        directions = [
                (2, 1),
                (2, -1),
                (-2, -1),
                (-2, 1),
                (1, 2),
                (-1, 2),
                (1, -2),
                (-1, -2)]
        for direction in directions:
            row = self.pos[0] + direction[0]
            column = self.pos[1] + direction[1]
            if not (0 <= row <= 7 and 0 <= column <= 7):
                continue

            piece = piece_info_func((row, column))
            if piece is not None:
                if piece[1] != self.color:
                    pseudo_legal_moves.add((row, column))
            else:
                pseudo_legal_moves.add((row, column))
        self.pseudo_legal_moves = pseudo_legal_moves


class Queen(Piece):

    @property
    def type(self):
        return PieceCode.QUEEN

    def update_pseudo_legal_moves(
            self,
            piece_info_func,
            en_passant,
            castling):
        pseudo_legal_moves = set()
        directions = [
                (-1, 0),
                (0, 1),
                (1, 0),
                (0, -1),
                (1, 1),
                (1, -1),
                (-1, 1),
                (-1, -1)]
        distance = 1
        while len(directions) > 0:
            for direction in directions.copy():
                row = self.pos[0] + direction[0] * distance
                column = self.pos[1] + direction[1] * distance
                if not (0 <= row <= 7 and 0 <= column <= 7):
                    directions.remove(direction)
                    continue
                piece = piece_info_func((row, column))
                if piece is not None:
                    directions.remove(direction)
                    if piece[1] != self.color:
                        pseudo_legal_moves.add((row, column))
                else:
                    pseudo_legal_moves.add((row, column))
            distance += 1
        self.pseudo_legal_moves = pseudo_legal_moves


class King(Piece):

    def __init__(self, color: PieceColor, pos: (int, int)):
        super(King, self).__init__(color, pos)
        self.first_move = True

    def notify_move(
            self,
            pos: (int, int),
            piece_info_func,
            en_passant,
            castling) -> (MoveNotification, any):

        old_pos = self.pos
        notify = super(King, self).notify_move(
                pos,
                piece_info_func,
                en_passant,
                castling)

        if self.first_move:

            # castling performed
            if abs(old_pos[1] - pos[1]) == 2:
                castling_type = ['q', 'k'][pos[1] > 3]
                castling_type = MoveNotification(castling_type)
                old_rook_idx = (old_pos[0], [0, 7][castling_type.value == 'k'])
                new_rook_idx = (old_pos[0], int((old_pos[1] + pos[1])/2))
                notify = (
                        castling_type,
                        {
                            'old': old_rook_idx,
                            'new': new_rook_idx,
                        })
            # revoke castling rights
            else:
                notify = (MoveNotification.BREAK_CASTLING, notify[1])

        self.first_move = False
        return notify

    @property
    def type(self):
        return PieceCode.KING

    def update_pseudo_legal_moves(
            self,
            piece_info_func,
            en_passant,
            castling):
        pseudo_legal_moves = set()
        directions = [
                (-1, 0),
                (0, 1),
                (1, 0),
                (0, -1),
                (1, 1),
                (1, -1),
                (-1, 1),
                (-1, -1)]
        for direction in directions:
            row = self.pos[0] + direction[0]
            column = self.pos[1] + direction[1]
            if not (0 <= row <= 7 and 0 <= column <= 7):
                continue
            piece = piece_info_func((row, column))
            if piece is not None:
                if piece[1] != self.color:
                    pseudo_legal_moves.add((row, column))
            else:
                pseudo_legal_moves.add((row, column))

        # check if castling is available
        if self.first_move:
            available_castlings = [
                    MoveNotification(v.lower()) for v in castling]
            directions = []
            if MoveNotification.KING_CASTLING in available_castlings:
                directions.append(1)
            if MoveNotification.QUEEN_CASTLING in available_castlings:
                directions.append(-1)
            for direction in directions:
                # 1. you can't castle if you moved
                # 2. you can't castle out of check
                # 3. you can't castle through check
                # 4. you can't castle through pieces
                has_piece_between = False
                rook_idx = [0, 7][direction == 1]
                initial = self.pos[1] + direction
                for column in range(initial, rook_idx, direction):
                    if piece_info_func((self.pos[0], column)) is not None:
                        has_piece_between = True
                        break
                if not has_piece_between:
                    pseudo_legal_moves.add(
                            (self.pos[0], self.pos[1] + 2 * direction))

        self.pseudo_legal_moves = pseudo_legal_moves


class Rook(Piece):

    def __init__(self, color: PieceColor, pos: (int, int)):
        super(Rook, self).__init__(color, pos)
        # will get its value on the first move
        self.first_move = True
        self.castling_type = MoveNotification(['q', 'k'][pos[1] > 3])

    def notify_move(
            self,
            pos: (int, int),
            piece_info_func,
            en_passant,
            castling) -> (MoveNotification, any):

        old_pos = self.pos
        notify = super(Rook, self).notify_move(
                pos,
                piece_info_func,
                en_passant,
                castling)

        # if there is a king next to us (from the side we
        # came from), then a castling just happened
        if self.first_move:
            if old_pos[0] == pos[0] and self.castling_type.value in castling:
                direction = [-1, 1][
                        self.castling_type == MoveNotification.KING_CASTLING]
                neighbour_piece = piece_info_func((pos[0], pos[1] + direction))
                # if its not None we know its the king
                # since we can't pass through pieces
                if neighbour_piece is not None:
                    notify = (MoveNotification.BREAK_CASTLING, notify[1])
            # castling has been broken in this side at least
            else:
                notify = (
                        MoveNotification(self.castling_type.value.upper()),
                        notify[1])

        self.first_move = False
        return notify

    @property
    def type(self):
        return PieceCode.ROOK

    def update_pseudo_legal_moves(
            self,
            piece_info_func,
            en_passant,
            castling):
        pseudo_legal_moves = set()
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        distance = 1
        while len(directions) > 0:
            for direction in directions.copy():
                row = self.pos[0] + direction[0] * distance
                column = self.pos[1] + direction[1] * distance
                if not (0 <= row <= 7 and 0 <= column <= 7):
                    directions.remove(direction)
                    continue
                piece = piece_info_func((row, column))
                if piece is not None:
                    directions.remove(direction)
                    if piece[1] != self.color:
                        pseudo_legal_moves.add((row, column))
                else:
                    pseudo_legal_moves.add((row, column))
            distance += 1
        self.pseudo_legal_moves = pseudo_legal_moves


class Bishop(Piece):

    @property
    def type(self):
        return PieceCode.BISHOP

    def update_pseudo_legal_moves(
            self,
            piece_info_func,
            en_passant,
            castling):
        pseudo_legal_moves = set()
        directions = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
        distance = 1
        while len(directions) > 0:
            for direction in directions.copy():
                row = self.pos[0] + direction[0] * distance
                column = self.pos[1] + direction[1] * distance
                if not (0 <= row <= 7 and 0 <= column <= 7):
                    directions.remove(direction)
                    continue
                piece = piece_info_func((row, column))
                if piece is not None:
                    directions.remove(direction)
                    if piece[1] != self.color:
                        pseudo_legal_moves.add((row, column))
                else:
                    pseudo_legal_moves.add((row, column))
            distance += 1
        self.pseudo_legal_moves = pseudo_legal_moves


def piece_class_from_code(code: PieceCode):
    if code == PieceCode.QUEEN:
        return Queen
    elif code == PieceCode.KING:
        return King
    elif code == PieceCode.KNIGHT:
        return Knight
    elif code == PieceCode.ROOK:
        return Rook
    elif code == PieceCode.BISHOP:
        return Bishop
    elif code == PieceCode.PAWN:
        return Pawn
