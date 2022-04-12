from tile import Tile
from piece import PieceDrawer


class GameBoardGraphical():
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

    def draw(self, surface, piece_info_func):
        for i, row in enumerate(self.tiles):
            for j, tile in enumerate(row):
                tile.draw(surface)
                piece_info = piece_info_func(i, j)
                if piece_info is not None:
                    piece_code, piece_color = piece_info
                    PieceDrawer.draw(tile.surf, piece_code, piece_color)

    def tile_info(self, i, j):
        tile = self.tiles[i][j]
        topleft_coords = (
                self._coords[0] + self.tile_side * j,
                self._coords[1] + self.tile_side * i)
        return tile.surf.get_rect(topleft=topleft_coords), tile.surf

    def update_graphical_attributes(
            self,
            dims: (int, int),
            coords: (int, int)):
        self._calculate_coords(dims, coords)
        self.update_tiles()
        PieceDrawer.resize((self.tile_side, self.tile_side))

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
