#!/usr/bin/env python3
from enum import Enum

from tile import Tile
from piece import PieceColor, PieceCode
from piece import piece_class_from_code


class GameBoardTurn(Enum):
    WHITE = 'w'
    BLACK = 'b'


class GameBoard():
    def __init__(
            self,
            dims: (int, int),
            coords: (int, int),
            color: (int, int, int)):
        '''
        game board will take the dimensions and coordinates given and calculate
        appropriate ones to maintain the aspect ratio. Because of this, we have
        'self._given_coords' and 'self._coords', where the coordinates given as
        input and the ones calculated are stored, respectively
        '''
        self._color = color
        self._given_coords = coords
        self.tiles = self.create_blank_tiles()
        self.update_graphical_attributes(dims, coords)

        # fen code attributes
        self.turn = 'w'
        self.castling = '-'
        self.halfmoves = 0
        self.fullmoves = 0

    def set_initial_fen(self):
        self.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - 0 0")

    def set_fen(self, fen_code):
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
                    self.tiles[i][j].piece = piece_class(color)
                    j += 1
                else:
                    j += int(c)

        # game attributes (turn, castling, en passant)
        attrs = attrs.split(' ')
        self.turn = attrs[0]
        self.castling = attrs[1]
        self.halfmoves = int(attrs[2])
        self.fullmoves = int(attrs[3])

    def get_fen(self):
        fen = ""
        for row in self.tiles:
            empty = 0
            for tile in row:
                if tile.piece is None:
                    empty += 1
                else:
                    if empty != 0:
                        fen += str(empty)
                    if tile.piece.color == PieceColor.WHITE:
                        fen += tile.piece.type.value.upper()
                    elif tile.piece.color == PieceColor.BLACK:
                        fen += tile.piece.type.value.lower()
            if empty != 0:
                fen += str(empty)

            fen += '/'

        # remove last '/'
        fen = fen[:-1]

        fen += " " + self.turn
        fen += " " + self.castling
        fen += " " + str(self.halfmoves)
        fen += " " + str(self.fullmoves)
        return fen

    def draw(self, surface):
        for row in self.tiles:
            for tile in row:
                tile.draw(surface)

    def update_graphical_attributes(
            self,
            dims: (int, int),
            coords: (int, int)):
        self._calculate_coords(dims, coords)
        self.update_tiles()

    def _calculate_coords(self, dims, coords):
        # get lowest dimension to define sizes
        self.tile_side = min(dims[0], dims[1])/8
        self._dims = dims

        # get coordinates that fit inside space given
        middle_point = (coords[0] + dims[0]/2, coords[1] + dims[1]/2)

        self._coords = (
                middle_point[0] - 4 * self.tile_side,
                middle_point[1] - 4 * self.tile_side)

    def create_blank_tiles(self):
        tiles = []
        for i in range(8):
            tiles.append([])
            for j in range(8):
                tile = Tile(dims=(1, 1), coords=(0, 0), color=(0, 0, 0))
                tiles[i].append(tile)
        return tiles

    def update_tiles(self):
        for i in range(len(self.tiles)):
            for j in range(len(self.tiles[0])):
                self.update_tile(self.tiles[i][j], i, j)

    def update_tile(self, tile, row_idx, column_idx):
        y = self.coords[1] + row_idx * self.tile_side
        x = self.coords[0] + column_idx * self.tile_side
        color_factor = 0.5 if (row_idx+column_idx) % 2 == 0 else 1
        current_color = (
                self.color[0] * color_factor,
                self.color[1] * color_factor,
                self.color[2] * color_factor)
        tile.dims = (self.tile_side, self.tile_side)
        tile.coords = (x, y)
        tile.color = current_color

    @property
    def dims(self):
        return self._dims

    @property
    def coords(self):
        return self._coords

    @property
    def color(self):
        return self._color

    @dims.setter
    def dims(self, d: (int, int)):
        self._dims = d
        self.update_graphical_attributes(self._dims, self._given_coords)

    @coords.setter
    def coords(self, c: (int, int)):
        self._given_coords = c
        self.update_graphical_attributes(self.dims, self._given_coords)

    @color.setter
    def color(self, c: (int, int, int)):
        self._color = c
        self.update_graphical_attributes(self.dims, self._given_coords)
