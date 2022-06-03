import pygame
import threading
import time


from piece import PieceColor
from tile import Tile


class GameBoardTimer:
    def __init__(
            self,
            dims: (int, int),
            coords: (int, int),
            bottom_color: PieceColor,
            settings: dict,
            out_of_time_func):
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self._bottom_color = bottom_color
        self.settings = settings
        self._given_coords = coords
        self.tiles: dict = self.create_blank_tiles()
        self.update_graphical_attributes(dims, coords)

        self.time_left = {
                PieceColor.BLACK: settings['timer'] * 1000,
                PieceColor.WHITE: settings['timer'] * 1000
                }
        self.out_of_time_func = out_of_time_func
        self.current_player = PieceColor.WHITE
        self.last_num_ticks = 0
        self.paused = True
        self.thread = threading.Thread(target=self.run)

    def unpause(self):
        self.last_num_ticks = pygame.time.get_ticks()
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def pause(self):
        self.paused = True
        self.thread.join()

    def run(self):
        self.paused = False
        self.last_num_ticks = pygame.time.get_ticks()
        while not self.paused:
            now = pygame.time.get_ticks()
            diff = now - self.last_num_ticks
            self.time_left[self.current_player] -= diff
            if self.time_left[self.current_player] < 0:
                self.out_of_time_func()
                return
            self.last_num_ticks = now
            time.sleep(0.1)

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

    def draw(self, surface):
        for k in self.time_left:
            color = [(255, 255, 255), (0, 0, 0)][k != PieceColor.BLACK]
            time_left = self.time_left[k]
            seconds = time_left//1000
            minutes = seconds//60
            seconds = seconds % 60
            text_surface = self.font.render(
                    "{0:02d}:{1:02d}".format(minutes, seconds),
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
            row = [1, 8][k == self.bottom_color]
            self.tiles[k].dims = (self.tile_side * 3, self.tile_side * 1)
            self.tiles[k].coords = (
                    self.coords[0] + self.tile_side,
                    self.coords[1] + row * self.tile_side)

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
