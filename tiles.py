from random import choice, randint
import pygame

from settings import SCREEN_WIDTH, TILE_SIZE
from supports import import_folder


class Tile(pygame.sprite.Sprite):
    def __init__(self, sprite_type, pos, groups) -> None:
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.pos = pos
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)

        self.display_surface = pygame.display.get_surface()


class SurfTile(Tile):
    def __init__(self, sprite_type, pos, groups, surface) -> None:
        super().__init__(sprite_type, pos, groups)
        self.image = surface


class AnimatedTile(Tile):
    def __init__(self, sprite_type, pos, groups, path):
        super().__init__(sprite_type, pos, groups)
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


class CircularSpike(SurfTile):
    def __init__(self, sprite_type, pos, groups, surface) -> None:
        super().__init__(sprite_type, pos, groups, surface)
        self.original_image = surface
        self.rect = self.image.get_rect(center=pos)
        self.death_box = self.rect.inflate(-10, -10)
        self.rotation_deg = 0
        self.turn_speed = choice([5, 8, 10])

    def rotate(self):
        self.rotation_deg += self.turn_speed
        if self.rotation_deg >= 360:
            self.rotation_deg = 0

        self.image = pygame.transform.rotate(
            self.original_image, -self.rotation_deg)
        self.rect = self.image.get_rect(center=self.pos)
        self.death_box = self.rect.inflate(-16, -16)
        # pygame.draw.rect(self.display_surface, 'red', self.death_box, 1)

    def update(self):
        self.rotate()


class LargeSpike(AnimatedTile):
    def __init__(self, sprite_type, pos, groups, path, direction):
        super().__init__(sprite_type, pos, groups, path)
        self.direction = direction
        self.last_time = pygame.time.get_ticks()
        self.can_animate = False

        # Update rect
        if self.direction == "up":
            self.rect = self.image.get_rect(
                bottomleft=(self.pos[0], self.pos[1] + TILE_SIZE))
        elif self.direction == 'left':
            self.rect = self.image.get_rect(
                topright=(self.pos[0] + TILE_SIZE, self.pos[1]))
        else:
            self.rect = self.image.get_rect(topleft=self.pos)

    def update(self):
        current_time = pygame.time.get_ticks()

        # print(current_time, self.last_time)
        # if current_time - self.last_time >= 1000:
        #     print(int(self.frame_index), len(self.frames))
        #     if int(self.frame_index) == 0:
        #         self.last_time = current_time
        #         print("No animation")

        #     self.animate()

        # Update rect
        if self.direction == "up":
            self.rect = self.image.get_rect(
                bottomleft=(self.pos[0], self.pos[1] + TILE_SIZE))
        elif self.direction == 'left':
            self.rect = self.image.get_rect(
                topright=(self.pos[0] + TILE_SIZE, self.pos[1]))
        else:
            self.rect = self.image.get_rect(topleft=self.pos)

        # pygame.draw.rect(self.display_surface, 'red', self.rect, 1)


class SquareSpike(SurfTile):
    def __init__(self, sprite_type, pos, groups, surface, obstacle_sprites, direction):
        super().__init__(sprite_type, pos, groups, surface)
        self.obstacle_sprites = obstacle_sprites
        self.direction_type = direction
        self.speed = 2
        self.direction = pygame.Vector2()

    def move(self):
        if self.direction_type == 'vertical':
            self.direction.x = self.speed
            self.rect.x += self.direction.x

        elif self.direction_type == 'horizontal':
            self.direction.y = self.speed
            self.rect.y += self.direction.y

    def collision(self):
        for obstacle_sprite in self.obstacle_sprites:
            if obstacle_sprite.rect.colliderect(self.rect):
                self.speed = -self.speed

    def update(self):
        self.move()
        self.collision()

        # pygame.draw.rect(self.display_surface, 'red', self.rect, 1)


class MapLoaderRect(pygame.sprite.Sprite):
    def __init__(self, pos, groups) -> None:
        super().__init__(groups)
        self.sprite_type = 'map_loader'
        self.image = pygame.Surface((SCREEN_WIDTH, TILE_SIZE))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft=pos)
