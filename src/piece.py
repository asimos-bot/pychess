#!/usr/bin/env python3
import pygame
from abc import ABC
from abc import abstractmethod
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


class Piece(ABC):

    def __init__(self, color: PieceColor):
        self.color = color
        self.load_image()

    def draw(self, surface):
        surface.blit(self.image, (0, 0))

    def load_image(self):
        self.filepath = Path(__file__).parent.parent
        self.filepath = self.filepath.joinpath("imgs")
        filename = self.color.name.lower()
        filename += "_"
        filename += self.type.name.lower()
        filename += ".png"
        self.filepath = self.filepath.joinpath(filename)

        self._image = pygame.image.load(self.filepath).convert_alpha()

    def resize(self, dims):
        self._image = pygame.image.load(self.filepath).convert_alpha()
        self._image = pygame.transform.scale(self._image, dims)

    @property
    def image(self):
        return self._image

    @property
    @abstractmethod
    def type(self) -> PieceCode:
        pass


class Pawn(Piece):

    @property
    def type(self):
        return PieceCode.PAWN


class Knight(Piece):

    @property
    def type(self):
        return PieceCode.KNIGHT


class Queen(Piece):

    @property
    def type(self):
        return PieceCode.QUEEN


class King(Piece):

    @property
    def type(self):
        return PieceCode.KING


class Rook(Piece):

    @property
    def type(self):
        return PieceCode.ROOK


class Bishop(Piece):

    @property
    def type(self):
        return PieceCode.BISHOP


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
