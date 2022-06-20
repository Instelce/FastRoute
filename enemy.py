import os
import pygame
import math

from settings import TILE_SIZE
from supports import import_folder, read_json_file


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, pos, groups) -> None:
        super().__init__(groups)

        # Setup
        self.type = enemy_type
        self.pos = pos
        self.import_graphics()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=self.pos)

        # Stats
        self.enemy_stats = read_json_file('data/enemies.json')[self.type]
        self.action_range = self.enemy_stats['action_range']
        self.action_range_rect = pygame.Rect(
            self.rect.center[0] - self.action_range / 2, self.rect.center[1] - self.action_range / 2, self.action_range, self.action_range)

        # Aura
        self.aura_origin_image = pygame.image.load(
            'graphics/enemies/aura.png').convert_alpha()
        self.aura_image = self.aura_origin_image
        self.aura_grow = 1

        # Aim zone
        self.aim_zone = None
        self.aim_zone_exist = False

        self.bullet_exist = False

        # Animations
        self.status = 'look_front'
        self.animation_speed = 0.15
        self.frame_index = 0

        self.last_time = pygame.time.get_ticks()
        self.display_surface = pygame.display.get_surface()

    def import_graphics(self):
        enemy_path = f'graphics/enemies/{self.type}/'
        animations_dir = os.scandir(enemy_path)
        self.animations = {}

        for dir in animations_dir:
            self.animations[dir.name] = []

        for animation in self.animations:
            full_path = enemy_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        animation = self.animations[self.status]

        # Loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # Set the image
        self.image = animation[int(self.frame_index)]

    def behaviour(self, player, aim_zone_group, bullet_groups):
        pygame.draw.rect(self.display_surface, "red",
                         self.action_range_rect, 1)

        if self.type == 'sniper':
            if player.rect.y < self.rect.y:
                self.status = 'look_up'
            if player.rect.y > self.rect.y:
                self.status = 'look_down'

            if player.rect.x < self.rect.x:
                self.status = 'look_left'
            if player.rect.x > self.rect.x:
                self.status = 'look_right'

            if self.action_range_rect.colliderect(player.rect):
                self.status = 'shoot'

                # Create aim zone
                if not self.aim_zone_exist:
                    self.bullet_exist = False
                    self.aim_zone = AimZone(self, player, aim_zone_group)

                    if self.aim_zone.is_kill:
                        self.aim_zone_exist = False

                self.aim_zone_exist = True
            else:
                if self.aim_zone is not None:
                    self.aim_zone.kill()
                    self.aim_zone_exist = False

            if self.aim_zone is not None:
                if self.aim_zone.is_aim and not self.bullet_exist:
                    self.bullet = Bullet(
                        self.rect.center, player, bullet_groups)
                    self.bullet_exist = True
        elif self.type == 'pusher':
            pass

    def display_aura(self):
        current_time = pygame.time.get_ticks()

        # Set size of aura
        self.aura_size = self.aura_image.get_height()
        if current_time - self.last_time >= 40:
            if self.aura_size == 52:
                self.aura_grow = -1
            if self.aura_size == 44:
                self.aura_grow = 1
        self.aura_size += self.aura_grow

        # Scale aura
        self.aura_image = pygame.transform.scale(
            self.aura_origin_image, (self.aura_size, self.aura_size))

        # Display
        self.display_surface.blit(
            self.aura_image, (self.rect.center[0] - self.aura_size / 2, self.rect.center[1] - self.aura_size / 2))

    def update(self):
        self.display_aura()
        self.animate()


class AimZone(pygame.sprite.Sprite):
    def __init__(self, enemy, player, groups):
        super().__init__(groups)

        # Setup
        self.enemy_type = enemy.type
        self.status = enemy.status
        self.pos = enemy.rect.center
        self.player = player
        self.import_graphics()

        self.is_aim = False
        self.is_kill = False

        # Animation
        self.aim_speed = 1000
        self.frame_index = 0

        self.image = self.animations[self.status][0]
        self.rect = self.image.get_rect(midbottom=self.pos)

        self.last_time = pygame.time.get_ticks()

    def import_graphics(self):
        aim_zone_path = f'graphics/enemies/aim_zone/{self.enemy_type}/'
        animations_dir = os.scandir(aim_zone_path)
        self.animations = {}

        for dir in animations_dir:
            print(dir.name)
            self.animations[dir.name] = []

        for animation in self.animations:
            full_path = aim_zone_path + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self):
        animation = self.animations[self.status]
        current_time = pygame.time.get_ticks()

        if current_time - self.last_time >= self.aim_speed and self.frame_index < len(animation) - 1:
            self.last_time = current_time
            print(self.frame_index, '/', len(animation) - 1)
            self.frame_index += 1

        if current_time - self.last_time >= self.aim_speed and self.frame_index == len(animation) - 1:
            self.is_kill = True
            self.is_aim = True
            print("AIM ZONE KILL")
            self.kill()

        self.image = animation[self.frame_index]
        self.rect = self.image.get_rect(midbottom=self.pos)

    def rotate(self):
        mx, my = self.player.rect.center
        dx, dy = mx - self.rect.centerx + \
            self.player.camera_offset[0], self.rect.centery + \
            self.player.camera_offset[1] - my
        angle = math.degrees(math.atan2(-dy, dx)) + 90
        self.image = pygame.transform.rotate(self.image, -angle)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        self.animate()
        self.rotate()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, player, groups):
        super().__init__(groups)
        self.sprite_type = 'bullet'
        self.pos = pos
        self.player = player
        self.image = pygame.Surface((4, 6))
        self.image.fill("#e02323")
        self.rect = self.image.get_rect(center=pos)
        self.speed = 10
        self.direction = pygame.Vector2()

    def get_direction(self):
        enemy_pos = pygame.Vector2(self.pos)
        player_pos = pygame.Vector2(self.player.rect.center)

        distance = (player_pos - enemy_pos).magnitude()

        if distance > 0:
            self.direction = (player_pos - enemy_pos).normalize()
        else:
            self.direction = pygame.math.Vector2()

    def collide_player(self):
        if self.rect.colliderect(self.player.rect):
            self.kill()

    def update(self):
        self.get_direction()
        self.collide_player()

        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
