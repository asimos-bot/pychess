#!/usr/bin/env python3
import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(
            self,
            dims: (int, int) = (1, 1),  # height and length
            coords: (int, int) = (0, 0),  # x and y of the top left corner
            color: (int, int, int) = (0, 0, 0)):  # rgb value
        super(Tile, self).__init__()
        self._dims = dims
        self.coords = coords
        self._color = color
        self._piece = None

        self.resize()

    def draw(self, surface):
        surface.blit(self.surf, self.coords)
        if self._piece is not None:
            self._piece.draw(self.surf)

    def resize(self):
        self.surf = pygame.Surface(self._dims)
        self.surf.fill(self._color)

        if self._piece is not None:
            self._piece.resize(self.surf.get_size())

    @property
    def dims(self):
        return self._dims

    @property
    def color(self):
        return self._color

    @dims.setter
    def dims(self, d: (int, int)):
        self._dims = d
        self.resize()

    @color.setter
    def color(self, c: (int, int, int)):
        self._color = c
        self.surf.fill(self._color)

    @property
    def piece(self):
        return self._piece

    @piece.setter
    def piece(self, p):
        self._piece = p
        self.resize()
