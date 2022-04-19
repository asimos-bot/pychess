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


class PieceDrawer():

    @classmethod
    def load_images(cls):
        img_folder = Path(__file__).parent.parent.joinpath("imgs")
        imgs = dict()
        for color in PieceColor:
            imgs[color] = dict()
            for piece_code in PieceCode:
                filename = color.name.lower()
                filename += "_"
                filename += piece_code.name.lower()
                filename += ".png"
                filepath = img_folder.joinpath(filename)
                img = pygame.image.load(filepath).convert_alpha()
                imgs[color][piece_code] = {
                        'filepath': filepath,
                        'img': img
                    }
        cls.imgs = imgs

    @classmethod
    def resize(cls, dims):
        cls.load_images()
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

    def __init__(self, color: PieceColor):
        self.color = color

    @property
    @abstractmethod
    def type(self) -> PieceCode:
        pass

    @abstractmethod
    def get_valid_moves(self, pos, pieces):
        pass


class Pawn(Piece):

    @property
    def type(self):
        return PieceCode.PAWN

    def get_valid_moves(self, pos, pieces):
        return []


class Knight(Piece):

    @property
    def type(self):
        return PieceCode.KNIGHT

    
    def get_valid_moves(self, pos, pieces):
        move_list = [(2,1),(2,-1),(-2,-1),(-2,1),(1,2),(-1,2),(1,-2),(-1,-2)]
        possible_moves = []
        piece_color = pieces[pos[0]][pos[1]].color
        for move_index in move_list:
            if(0 <= pos[0] + move_index[0] <= 7 and 0 <= pos[1] + move_index[1] <= 7): 
                if (pieces[pos[0] + move_index[0]][pos[1] + move_index[1]] is None) or (piece_color != pieces[pos[0] + move_index[0]][pos[1] + move_index[1]].color): 
                    possible_moves.append((pos[0]+move_index[0],pos[1]+move_index[1]))
        
        return possible_moves


class Queen(Piece):

    @property
    def type(self):
        return PieceCode.QUEEN
    
    def get_valid_moves(self, pos, pieces):
        return []


class King(Piece):

    @property
    def type(self):
        return PieceCode.KING

    def get_valid_moves(self, pos, pieces):
        return []


class Rook(Piece):

    @property
    def type(self):
        return PieceCode.ROOK

    def get_valid_moves(self, pos, pieces):
        return []


class Bishop(Piece):
    
    @property
    def type(self):
        return PieceCode.BISHOP

    def get_valid_moves(self, pos, pieces):
        move_list = [(1,1),(-1,-1),(-1,1),(1,-1)]
        possible_moves = [] 
        piece_color = pieces[pos[0]][pos[1]].color
        for move_index in move_list:
            index_counter_x = move_index[0]
            index_counter_y = move_index[1]
            while (0 <= pos[0] + index_counter_x <= 7 and 0 <= pos[1] + index_counter_y <= 7): 
                if (pieces[pos[0] + index_counter_x][pos[1] + index_counter_y] is None) or (piece_color != pieces[pos[0] + move_index[0]][pos[1] + move_index[1]].color): 
                    possible_moves.append((pos[0]+index_counter_x,pos[1]+index_counter_y))
                    index_counter_x += move_index[0]
                    index_counter_y += move_index[1]
                else:
                    break

        return possible_moves


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
