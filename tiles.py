import pygame

from settings import TILE_SIZE


class Tile(pygame.sprite.Sprite):
    def __init__(self, sprite_type, pos, groups, surface) -> None:
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)