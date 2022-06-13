import sys
import pygame

from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from level import Level


class Game:
    def __init__(self) -> None:

        # Game setup
        pygame.init()
        pygame.display.set_caption("Fast Route")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Scenes
        self.status = 'level'
        self.scenes = {
            'level': Level()
        }

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # self.screen.fill('#0e071b')
            self.screen.fill('black')
            self.scenes[self.status].display()

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()