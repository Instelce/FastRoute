import math
import pygame
from debug import debug
from svg.path import parse_path

from settings import TILE_SIZE
from supports import import_folder


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, camera) -> None:
        super().__init__(groups)
        self.import_assets()

        # Setup
        self.sprite_type = 'player'
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.obstacle_sprites = obstacle_sprites

        self.is_aim = False
        self.direction = pygame.math.Vector2()
        self.gravity = 0.1
        self.force = 0
        self.max_force = 150
        self.min_force = 50
        self.shoot_count = 0
        self.in_air = False
        self.air_time = None
        self.max_air_time = 1000
        self.force_range = pygame.Rect(
            self.rect.centerx - 200, self.rect.centery - 200, 400, 400)
        self.first_move = False

        self.on_right = False
        self.on_left = False
        self.on_bottom = False
        self.on_top = False
        self.is_colliding = True

        # Animation
        self.status = 'normal'
        self.frame_index = 0
        self.animation_speed = 0.15

        # Camera
        self.camera = camera
        self.camera_offset = self.camera.get_offset()

        # Indicator
        self.indicator_original_image = pygame.image.load(
            'graphics/player/indicator.png').convert_alpha()
        self.indicator_image = self.indicator_original_image
        self.indicator_rect = self.indicator_image.get_rect(midbottom=(
            self.rect.centerx + self.camera_offset[0], self.rect.centery + self.camera_offset[1]))

        self.last_time = pygame.time.get_ticks()
        self.display_surface = pygame.display.get_surface()

    def import_assets(self):
        animation_path = 'graphics/player/'
        self.animations = {'normal': [], 'in_air': []}

        for animation in self.animations.keys():
            full_path = animation_path + animation
            self.animations[animation] = import_folder(full_path)

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and not self.is_aim and self.shoot_count < 2:
            self.force = 0
            # self.direction = pygame.math.Vector2()
            self.is_aim = True

            if self.shoot_count == 1:
                self.force = self.force // 5

            print(f'{self.shoot_count} Prepare the launch...')

        if not keys[pygame.K_SPACE] and self.is_aim:
            self.air_time = pygame.time.get_ticks()
            self.force = self.get_direction_force()[0]
            self.direction = self.get_direction_force()[1]
            self.is_aim = False
            self.in_air = True
            self.shoot_count += 1
            self.first_move = True

            print('Launched !')

        # if self.in_air:
        #     print("In air")
        #     if self.air_time - self.last_time >= self.max_air_time:
        #         print("Finish")
        #         self.force = self.min_force
        #         self.direction = pygame.Vector2()

    def get_status(self):
        if self.in_air:
            self.status = 'in_air'
        else:
            self.status = 'normal'

    def animate(self):
        animation = self.animations[self.status]

        # Loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # Set the image
        self.image = animation[int(self.frame_index)]
        # self.rect = self.image.get_rect(center=)

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Horizontal
        self.rect.x += self.direction.x * (speed / 10)
        self.collision('horizontal')

        # Vertical
        self.rect.y += self.direction.y * (speed / 10)
        self.collision('vertical')

        if self.is_colliding:
            self.force = 0
            self.direction = pygame.math.Vector2()
            self.shoot_count = 0
            self.in_air = False
            self.is_colliding = False

        self.rect.center = self.rect.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    self.is_colliding = True
                    print("Colliding", self.is_colliding)

                    if self.direction.x > 0:  # Right
                        self.rect.right = sprite.rect.left
                        self.on_right = True
                        self.current_x = self.rect.right
                    if self.direction.x < 0:  # Left
                        self.rect.left = sprite.rect.right
                        self.on_left = True
                        self.current_x = self.rect.left

            # Reset on_right and on_left
            if self.on_right and (self.rect.right < self.current_x or self.direction.x <= 0):
                self.on_right = False
            elif self.on_left and (self.rect.left < self.current_x or self.direction.x >= 0):
                self.on_left = False

        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.rect.colliderect(self.rect):
                    self.is_colliding = True

                    if self.direction.y > 0:  # Down
                        self.rect.bottom = sprite.rect.top
                        self.on_bottom = True
                    if self.direction.y < 0:  # Up
                        self.rect.top = sprite.rect.bottom
                        self.on_top = True

            # Reset on_bottom and on_top
            if self.on_bottom and self.direction.y < 0 or self.direction.y > 1:
                self.on_bottom = False
            elif self.on_top and self.direction.y > 0:
                self.on_top = False

            if self.shoot_count > 0 and not self.on_bottom and not self.on_top and not self.on_left and not self.on_right:
                self.apply_gravity()

    def get_direction_force(self):
        mouse_pos = (pygame.mouse.get_pos()[
                     0] - self.camera_offset[0], pygame.mouse.get_pos()[1] - self.camera_offset[1])
        player_vec = pygame.math.Vector2(self.rect.center)
        mouse_vec = pygame.math.Vector2(mouse_pos)
        force = 0

        if self.min_force < (mouse_vec - player_vec).magnitude() < self.max_force:
            force = (mouse_vec - player_vec).magnitude()
        else:
            if (mouse_vec - player_vec).magnitude() > self.max_force:
                force = self.max_force
            if (mouse_vec - player_vec).magnitude() < self.min_force:
                force = self.min_force

        if force > 0:
            direction = (mouse_vec - player_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (force, direction)

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def draw_indicator(self):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            force = self.get_direction_force()[0]
            direction = self.get_direction_force()[1]
            mouse_pos = pygame.mouse.get_pos()

            self.force_range = pygame.Rect(
                self.rect.centerx - 200 + self.camera_offset[0], self.rect.centery - 200 + self.camera_offset[1], 400, 400)

            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - self.rect.centerx + \
                self.camera_offset[0], self.rect.centery + \
                self.camera_offset[1] - my
            angle = math.degrees(math.atan2(-dy, dx)) + 90
            self.indicator_size = (
                self.indicator_original_image.get_size()[0], force)
            self.indicator_image = pygame.transform.scale(
                self.indicator_original_image, (self.indicator_size[0], math.floor(self.indicator_size[1])))

            if current_time - self.last_time >= 100:
                self.indicator_image = pygame.transform.rotate(
                    self.indicator_image, -angle)

            indicator_pos = (
                self.rect.center[0] + self.camera_offset[0], self.rect.center[1] + self.camera_offset[1])
            if -270 < -angle < -90:
                self.indicator_rect = self.indicator_image.get_rect(
                    center=indicator_pos)
            else:
                self.indicator_rect = self.indicator_image.get_rect(
                    center=indicator_pos)

            self.display_surface.blit(
                self.indicator_image, self.indicator_rect)

            # pygame.draw.line(self.display_surface, "white", indicator_pos, pygame.mouse.get_pos(), 2)

            # Debug
            debug(force, 100)
            debug(direction, 110)
            debug(-angle, 130)

    def update(self):
        self.camera_offset = self.camera.get_offset()

        self.get_status()
        self.animate()
        self.input()
        self.move(self.force)
