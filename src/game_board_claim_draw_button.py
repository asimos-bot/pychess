import pygame

from piece import PieceColor
from tile import Tile


class GameBoardClaimDrawButton:
    def __init__(
            self,
            dims: (int, int),
            coords: (int, int),
            bottom_color: PieceColor,
            settings: dict,
            claim_draw_func):
        self.active = False
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self._bottom_color = bottom_color
        self.settings = settings
        self._given_coords = coords
        self.claim_draw_func = claim_draw_func
        self.tile: dict = self.create_blank_tiles()
        self.update_graphical_attributes(dims, coords)

    def create_blank_tiles(self):
        if self.active:
            return Tile(color=(0, 0, 0))
        else:
            return Tile(color=self.settings['colors']['clear_screen'])

    def update_graphical_attributes(
            self,
            dims: (int, int),
            coords: (int, int)):

        self._calculate_coords(dims, coords)
        self.update_tiles()

    def draw(self, surface):
        color = (255, 255, 255)
        if not self.active:
            color = self.settings['colors']['clear_screen']
        text_surface = self.font.render(
                "Claim Draw",
                False,
                color)
        self.tile.draw(surface)
        surf = self.tile.surf
        surf.blit(text_surface, (0, 0))
        surface.blit(surf, self.tile.coords)

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
        row = 4.5
        self.tile.dims = (self.tile_side * 3, self.tile_side * 1)
        self.tile.coords = (
                self.coords[0] + self.tile_side,
                self.coords[1] + row * self.tile_side)

    def event_capture(self, event):
        if self.active:
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("is in the button?")
                mouse_pos = pygame.mouse.get_pos()
                tile_rect = self.tile.surf.get_rect(topleft=self.tile.coords)
                if tile_rect.collidepoint(mouse_pos):
                    print("hit")
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
