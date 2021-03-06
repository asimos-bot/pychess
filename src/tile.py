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

        self.resize()

    def draw(self, surface):
        surface.blit(self.surf, self.coords)
        self.surf.fill(self._color)

    def resize(self):
        self.surf = pygame.Surface(self._dims)
        self.surf.fill(self._color)

    @property
    def dims(self):
        return self._dims

    @dims.setter
    def dims(self, d: (int, int)):
        self._dims = d
        self.resize()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, c: (int, int, int)):
        self._color = c
        self.surf.fill(self._color)
