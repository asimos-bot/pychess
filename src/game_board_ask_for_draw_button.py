import pygame

from piece import PieceColor
from tile import Tile


class GameBoardAskForDrawButtons:
    def __init__(
            self,
            dims: (int, int),
            coords: (int, int),
            bottom_color: PieceColor,
            settings: dict,
            draw_agreed_func):
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self._bottom_color = bottom_color
        self.settings = settings
        self._given_coords = coords
        self.tiles: dict = self.create_blank_tiles()
        self.update_graphical_attributes(dims, coords)
        self.draw_agreed_func = draw_agreed_func

    def create_blank_tiles(self):
        return {
                PieceColor.WHITE: Tile(color=(255, 255, 255)),
                PieceColor.BLACK: Tile(color=(0, 0, 0))
                }

    def update_graphical_attributes(
            self,
            dims: (int, int),
            coords: (int, int)):

        self._calculate_coords(dims, coords)
        self.update_tiles()
        self.font = pygame.font.SysFont('Comic Sans MS', max(int(self.tile_side/1.6), 1))

    def draw(self, surface):
        for k in self.tiles:
            color = [(255, 255, 255), (0, 0, 0)][k != PieceColor.BLACK]

            text_surface = self.font.render(
                    "Request Draw",
                    False,
                    color)
            self.tiles[k].draw(surface)
            surf = self.tiles[k].surf
            surf.blit(text_surface, (0, 0))
            surface.blit(surf, self.tiles[k].coords)

    def _calculate_coords(self, dims, coords):

        top_spacing_percentage = self.settings['top_spacing_percentage']
        right_spacing_percentage = self.settings['right_spacing_percentage']
        # get lowest dimension to define sizes
        self.tile_side = min(
                dims[0] * (1 - right_spacing_percentage),
                dims[1] * (1 - top_spacing_percentage))/10
        self._dims = dims

        # get coordinates that fit inside space given
        middle_point = (
                coords[0] + (dims[0] * (1 - right_spacing_percentage))/2,
                coords[1] + (dims[1] * (1 + top_spacing_percentage))/2)

        self._coords = (
                middle_point[0] + 5 * self.tile_side,
                middle_point[1] - 5 * self.tile_side)

    def update_tiles(self):
        for k in self.tiles:
            row = [2.5, 6.5][k == self.bottom_color]
            self.tiles[k].dims = (self.tile_side * 3, self.tile_side * 1)
            self.tiles[k].coords = (
                    self.coords[0] + self.tile_side,
                    self.coords[1] + row * self.tile_side)

    def event_capture(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for k in self.tiles:
                tile_rect = self.tiles[k].surf.get_rect(topleft=self.tiles[k].coords)
                if tile_rect.collidepoint(mouse_pos):
                    self.claim_draw_func()
                    return

    @property
    def bottom_color(self):
        return self._bottom_color

    @bottom_color.setter
    def bottom_color(self, color: PieceColor):
        self._bottom_color = color
        self.update_tiles()

    @property
    def dims(self):
        return self._dims

    @dims.setter
    def dims(self, d: (int, int)):
        self._dims = d
        self.update_graphical_attributes(self._dims, self._given_coords)

    @property
    def coords(self):
        return self._coords

    @coords.setter
    def coords(self, c: (int, int)):
        self._given_coords = c
        self.update_graphical_attributes(self.dims, self._given_coords)
