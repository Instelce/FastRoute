from random import choice, randint
import pygame

from settings import SCREEN_WIDTH, TILE_SIZE
from supports import import_folder


class Tile(pygame.sprite.Sprite):
    def __init__(self, sprite_type, pos, groups, surface) -> None:
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.pos = pos
        self.image = surface
        self.rect = self.image.get_rect(topleft=pos)


class AnimatedTile(Tile):
    def __init__(self, sprite_type, pos, groups, surface, path):
        super().__init__(sprite_type, pos, groups, surface)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self):
        self.animate()

        
class CircularSpike(Tile):
    def __init__(self, sprite_type, pos, groups, surface) -> None:
        super().__init__(sprite_type, pos, groups, surface)
        self.original_image = surface
        self.rect = self.image.get_rect(center=pos)
        self.death_box = self.rect.inflate(-10, -10)
        self.rotation_deg = 0
        self.turn_speed = choice([5, 8, 10])

        self.display_surface = pygame.display.get_surface()
    
    def rotate(self):
        self.rotation_deg += self.turn_speed
        if self.rotation_deg >= 360:
            self.rotation_deg = 0

        self.image = pygame.transform.rotate(self.original_image, -self.rotation_deg)
        self.rect = self.image.get_rect(center=self.pos)
        self.death_box = self.rect.inflate(-16, -16)

    def update(self):
        self.rotate()


class MapLoaderRect(pygame.sprite.Sprite):
    def __init__(self, pos, groups) -> None:
        super().__init__(groups)
        self.sprite_type = 'map_loader'
        self.image = pygame.Surface((SCREEN_WIDTH, TILE_SIZE))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft=pos)