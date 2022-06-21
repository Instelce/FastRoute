import pygame
from random import randint


def circle_surf(radius, color):
    surf = pygame.Surface((radius * 2, radius * 2))
    pygame.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))
    return surf


class Particle():
    def __init__(self, startx, starty, add, color, radius, is_lighting=None):
        super().__init__()
        self.x = startx
        self.y = starty
        self.color = color
        self.sx = startx
        self.sy = starty
        self.add = add
        self.radius = radius
        self.is_lighting = False if is_lighting is None else is_lighting
        self.light_radius = self.radius * 2

    def move(self, particles):
        self.x += self.add[0]
        self.y += self.add[1]

        self.radius -= 0.1
        self.light_radius = self.radius * 2

        self.add[1] += 0.15

        if self.radius <= 0:
            particles.remove(self)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        if self.is_lighting:
            surface.blit(circle_surf(self.light_radius,
                                     (20, 20, 20)), (self.x - self.light_radius, self.y - self.light_radius), special_flags=pygame.BLEND_RGB_ADD)
