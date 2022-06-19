import pygame


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, pos, groups) -> None:
        super().__init__(groups)
        self.type = enemy_type
        self.pos = pos
        
    def update(self):
        pass
