#!/usr/bin/env python3
import pygame
from abc import ABC
from abc import abstractmethod
from enum import Enum


class PieceColor(Enum):
    WHITE = 1,
    BLACK = 2


class PieceCode(Enum):
    KING = 1,
    QUEEN = 2,
    KNIGHT = 3,
    BISHOP = 4,
    PAWN = 5
    TOWER = 6


class Piece(ABC):

    def draw(self, surface):
        surface.blit(self.image, (0, 0))

    def load_image(self):
        self.filename = "../imgs/"
        self.filename += self.color.name.lower()
        self.filename += "_"
        self.filename += self.type.name.lower()
        self.filename += ".png"

        self._image = pygame.image.load(self.filename).convert_alpha()

    def resize(self, dims):
        self._image = pygame.image.load(self.filename).convert_alpha()
        self._image = pygame.transform.scale(self._image, dims)

    @property
    def image(self):
        return self._image

    @property
    @abstractmethod
    def type(self) -> PieceCode:
        pass


class Pawn(Piece):

    def __init__(self, color: PieceColor):
        self.color = color
        self.load_image()

    @property
    def type(self):
        return PieceCode.PAWN
