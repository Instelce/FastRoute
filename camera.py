import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    def __init__(self, width, height):
        self.state = pygame.Rect(0, 0, width, height)
        
    def apply(self, target):
        return target.rect.move(self.state.topleft) 

    def func(self, camera, target_rect):

        # we want to center target_rect
        x = -target_rect.centerx + SCREEN_WIDTH/2
        y = -target_rect.centery + SCREEN_HEIGHT/2
        # move the camera. Let's use some vectors so we can easily substract/multiply
        camera.topleft += (pygame.Vector2((x, y)) - pygame.Vector2(camera.topleft[0], camera.topleft[1])) * 0.06 # add some smoothness coolnes
        # set max/min x/y so we don't see stuff outside the world
        camera.x = max(-(camera.width-SCREEN_WIDTH), min(0, camera.x))
        camera.y = max(-(camera.height-SCREEN_HEIGHT), min(0, camera.y))
        
        return camera

    def get_offset(self):
        return self.state.topleft

    def update(self, target):
        self.state = self.func(self.state, target.rect)