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
        self.old_status = self.status
        self.scene_transition = SceneTransition()
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
                        self.create_level_chooser_menu
                    ),
                    Button(
                        "Quit",
                        self.quit
                    )
                ],
                'graphics/ui/background.png'
            ),
            'level_chooser_menu': LevelChooserMenu(
                'complex',
                [
                    Text(
                        'midtop',
                        "Levels",
                        (SCREEN_WIDTH/2, 50),
                        UI_FONT,
                        TITLE_FONT_SIZE
                    ),
                ],
                'graphics/ui/background_two.png',
                self.create_level,
                self.create_start_menu
            ),
            'game_over_menu': Menu(
                'simple',
                [
                    Text(
                        'midtop',
                        "Game Over",
                        (SCREEN_WIDTH/2, SCREEN_HEIGHT/2-100),
                        UI_FONT,
                        TITLE_FONT_SIZE
                    ),
                    Button(
                        "Restart",
                        self.create_last_level
                    ),
                    Button(
                        "Levels",
                        self.create_level_chooser_menu
                    ),
                    Button(
                        "Quit",
                        self.quit
                    )
                ],
                'graphics/ui/background_two.png'
            ),
            'level': Level(1, self.create_level_chooser_menu, self.create_game_over_menu),
        }

    def create_start_menu(self):
        self.status = 'start_menu'
    
    def create_level_chooser_menu(self):
        self.scenes['level_chooser_menu'].create_level_buttons()
        self.status = 'level_chooser_menu'

    def create_game_over_menu(self):
        self.status = 'game_over_menu'

    def create_level(self, level_index):
        self.scenes['level'] = Level(level_index, self.create_level_chooser_menu, self.create_game_over_menu)
        self.level_index = level_index
        self.status = 'level'
    
    def create_last_level(self):
        self.scenes['level'] = Level(self.level_index, self.create_level_chooser_menu, self.create_game_over_menu)
        self.status = 'level'

    def quit(self):
        pygame.quit()
        sys.exit()

    def display_scene(self):
        if self.old_status != self.status:
            self.scenes[self.old_status].display()
            self.scene_transition.start()

            if self.scene_transition.can_dicrease:
                self.old_status = self.status

        if self.old_status == self.status:
            self.scenes[self.status].display()
            self.scene_transition.end()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            # self.screen.fill('#0e071b')
            self.screen.fill('black')
            self.display_scene()

            pygame.display.update()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()