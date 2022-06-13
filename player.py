import pygame
from debug import debug

from settings import TILE_SIZE


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites) -> None:
        super().__init__(groups)

        # Setup
        self.sprite_type = 'player'
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.obstacle_sprites = obstacle_sprites

        self.image.fill('orange')

        self.is_aim = False
        self.direction = pygame.math.Vector2()
        self.gravity = 0.2
        self.force = 0
        self.shoot_count = 0
        self.on_air = False

        self.on_right = False
        self.on_left = False
        self.on_bottom = False
        self.on_top = False
        self.is_colliding = True

        self.diplay_surface = pygame.display.get_surface()

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and not self.is_aim and self.shoot_count < 2:
            self.force = 0
            self.direction = pygame.math.Vector2()
            self.is_aim = True

            print('Prepare the launch...')

        if keys[pygame.K_SPACE]:
            pygame.draw.line(self.diplay_surface, 'white', (self.rect.centerx, self.rect.centery), pygame.mouse.get_pos(), 2)
            debug(self.get_direction_force()[0], 60)
            debug(self.get_direction_force()[1], 70)

        if not keys[pygame.K_SPACE] and self.is_aim:
            self.force = self.get_direction_force()[0]
            self.direction = self.get_direction_force()[1]
            self.is_aim = False
            self.shoot_count += 1

            print('Launched !')

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Horizontal
        self.rect.x += self.direction.x * (speed/10)
        self.collision('horizontal')

        # Vertical
        self.rect.y += self.direction.y * (speed/10)
        self.collision('vertical')
        
        if self.is_colliding:
            self.force = 0
            self.direction = pygame.math.Vector2()
            self.is_colliding = False
            self.shoot_count = 0

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

            if self.shoot_count > 0 and not self.is_aim and not self.on_bottom and not self.on_top and not self.on_left and not self.on_right:
                self.apply_gravity()

    def get_direction_force(self):
        mouse_pos = pygame.mouse.get_pos()
        player_vec = pygame.math.Vector2(self.rect.center)
        mouse_vec = pygame.math.Vector2(mouse_pos)

        if (mouse_vec - player_vec).magnitude() < 150:
            force = (mouse_vec - player_vec).magnitude()
        else:
            force = 150

        if force > 0:
            direction = (mouse_vec - player_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (force, direction)

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

    def update(self):
        self.input()
        self.move(self.force)