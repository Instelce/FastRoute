import pygame

from settings import SCREEN_WIDTH, TILE_SIZE


class Tile(pygame.sprite.Sprite):
    def __init__(self, sprite_type, pos, groups, surface) -> None:
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)
        
        
class Spike(Tile):
    def __init__(self, sprite_type, pos, groups, surface) -> None:
        super().__init__(sprite_type, pos, groups, surface)


class MapLoaderRect(pygame.sprite.Sprite):
    def __init__(self, pos, groups) -> None:
        super().__init__(groups)
        self.sprite_type = 'map_loader'
        self.image = pygame.Surface((SCREEN_WIDTH, TILE_SIZE))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft=pos)