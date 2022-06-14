import sys
import pygame

from menu import *
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
        self.create_start_menu()
        self.scenes = {
            'start_menu': Menu(
                'simple',
                [
                    Text(
                        'midtop',
                        "Fast Route",
                        (SCREEN_WIDTH/2, SCREEN_HEIGHT/2-100),
                        UI_FONT,
                        TITLE_FONT_SIZE
                    ),
                    Button(
                        "Levels",
                        self.create_level
                    ),
                    Button(
                        "Quit",
                        self.quit
                    )
                ],
                'graphics/ui/background.png'
            ),
            'level': Level(),
        }

    def create_start_menu(self):
        self.status = 'start_menu'

    def create_level(self):
        self.status = 'level'

    def quit(self):
        pygame.quit()
        sys.exit()

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