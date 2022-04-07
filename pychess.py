import pygame
import pygame.locals


class Rect(pygame.sprite.Sprite):
    def __init__(self, dimensions: (int, int), coords: (int, int)):
        super(Rect, self).__init__()
        self.surf = pygame.Surface(dimensions)
        self.surf.fill((0, 200, 255))
        self.rect = self.surf.get_rect()
        self.coords = coords


pygame.init()

rect = Rect((20, 20), (20, 20))

screen = pygame.display.set_mode((800, 600))

quit = False

while not quit:
    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT:
            quit = True
        elif event.type == pygame.locals.KEYDOWN:
            if event.key == pygame.locals.K_BACKSPACE:
                quit = True

    screen.blit(rect.surf, rect.coords)
    pygame.display.flip()
