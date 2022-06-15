import pygame
from math import floor

from settings import *
from supports import read_json_file


class Menu:
    def __init__(self, menu_type, components, background) -> None:
        print("Init Menu")

        self.menu_type = menu_type
        self.components = components
        self.background_path = background
        self.background = pygame.transform.scale(
            pygame.image.load(self.background_path).convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.display_surface = pygame.display.get_surface()

    def components_reposition(self):
        positionned = False

        if not positionned:
            start_pos = list(self.components[0].pos)

            for i in range(len(self.components)):
                if i >= 1:
                    component = self.components[i]
                    component_pos = list(component.pos)
                    component_size = list(self.components[i].size)

                    # Repos component
                    new_pos = start_pos[1] + component_size[1] + COMPONENTS_GAP * i
                    component_pos[1] = new_pos
                    component.pos = tuple(component_pos)

                positionned = True

    def display_components(self):
        for component in self.components:
            component.display()

    def draw_text(self, text, font, font_size, color, pos):
        font = pygame.font.Font(font, font_size)
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(midtop=pos)
        self.display_surface(text_surf, text_rect)

    def display(self):
        self.components_reposition()

        self.display_surface.blit(self.background, (0, 0))
        self.display_components()


class LevelChooserMenu(Menu):
    def __init__(self, menu_type, components, background, create_level, create_start_menu) -> None:
        super().__init__(menu_type, components, background)
        self.create_level = create_level
        self.create_start_menu = create_start_menu

        self.back_button = Button(
            "Back",
            self.create_start_menu,
            (SCREEN_WIDTH/2, SCREEN_HEIGHT-100)
        )

        self.create_level_buttons()

    def create_level_buttons(self):
        self.level_data = read_json_file('data/levels.json')
        self.level_buttons = []

        lines_counter = 0
        gap = 20
        button_size = 80
        
        for index, level in enumerate(self.level_data):
            self.level_buttons.append(Button(
                index+1,
                self.create_level,
                (SCREEN_WIDTH/2 - (button_size * 2 + gap + gap/2) + ((button_size + gap) * (index%4)), 150 + (button_size + gap) * lines_counter),
                'topleft',
                r"graphics\ui\buttons\level\default.png",
                r"graphics\ui\buttons\level\hover.png",
                r"graphics\ui\buttons\level\disable.png"
            ))
            if not self.level_data[level]['unlocked']:
                self.level_buttons[index].disable = True
            else:
                self.level_buttons[index].disable = False

            self.level_buttons[index].callback_arg = index+1

            # print(len(self.level_buttons), index+1 % 4, index)

            if (index+1) % 4 == 0:
                lines_counter += 1

    def display(self):
        self.components_reposition()

        self.display_surface.blit(self.background, (0, 0))
        self.display_components()

        # Back button
        self.back_button.display()

        # Draw buttons
        for button in self.level_buttons:
            button.display()


class SceneTransition:
    def __init__(self) -> None:
        self.display_surface = pygame.display.get_surface()
        self.last_time = pygame.time.get_ticks()

        self.size = 0

        self.transition_is_finish = False
        self.can_dicrease = False
        self.cooldown = 1
        self.grow = 50

    def start(self):
        self.loading_text = Text('midtop', "Fast Route", (SCREEN_WIDTH/2, SCREEN_HEIGHT/2), UI_FONT, floor(self.size/20), 'black')

        if self.transition_is_finish:
            self.transition_is_finish = False
            self.can_dicrease = False
            self.size = 100

        max_size = SCREEN_WIDTH + (SCREEN_WIDTH/3)

        current_time = pygame.time.get_ticks()

        if not self.transition_is_finish:
            if self.size <= max_size:
                if current_time - self.last_time >= self.cooldown:
                    self.last_time = current_time
                    self.size += self.grow

                    if self.size >= max_size:
                        self.can_dicrease = True

            pygame.draw.rect(self.display_surface, 'white', pygame.Rect(0, 0, self.size, SCREEN_HEIGHT))
            
            if self.size >= SCREEN_WIDTH/2:
                self.loading_text.display()

    def end(self):
        self.loading_text = Text('midtop', "Fast Route", (SCREEN_WIDTH/2, SCREEN_HEIGHT/2), UI_FONT, floor(self.size/20), 'black')

        if not self.transition_is_finish:
            current_time = pygame.time.get_ticks()
            
            if current_time - self.last_time >= self.cooldown:
                self.last_time = current_time
                self.size -= self.grow

                if self.size <= 0:
                    self.size = 0
                    self.transition_is_finish = True

            pygame.draw.rect(self.display_surface, 'white', pygame.Rect(SCREEN_WIDTH-self.size, 0, self.size, SCREEN_HEIGHT))
            
            if self.size >= SCREEN_WIDTH/2:
                self.loading_text.display()


class Button:
    def __init__(self, content, callback=None, pos=None, rect_alignement='midtop', default_image="graphics/ui/buttons/default/default.png", hover_image="graphics/ui/buttons/default/hover.png", disable_image="graphics/ui/buttons/default/disable.png") -> None:
        self.content = str(content)
        self.callback = callback
        self.pos = (SCREEN_WIDTH/2, 200) if pos is None else pos
        self.rect_alignement = rect_alignement

        self.display_surface = pygame.display.get_surface()
        self.callback_arg = None
        self.click = False
        self.disable = False

        # Image
        self.default_image = default_image
        self.hover_image = hover_image
        self.disable_image = disable_image
        self.image = pygame.image.load(self.default_image).convert_alpha()
        self.size = self.image.get_size()

        # Text
        self.text_color = 'white'

    def check_hover_click(self):
        mouse_pos = pygame.mouse.get_pos()

        # Hover
        if self.disable:
            self.image = pygame.image.load(self.disable_image).convert_alpha()
            self.display_surface.blit(self.image, self.rect)
            self.text_color = '#3f3f3f'
        else:
            if self.rect.collidepoint(mouse_pos):
                self.image = pygame.image.load(self.hover_image).convert_alpha()
                self.display_surface.blit(self.image, self.rect)
                
                self.text_color = 'white'

                # Click
                if pygame.mouse.get_pressed()[0]:
                    self.click = True
                    if self.callback != None:
                        if self.callback_arg != None:
                            self.callback(self.callback_arg)
                        else:
                            self.callback()
                else:
                    self.click = False
            else:
                self.image = pygame.image.load(self.default_image).convert_alpha()
                self.display_surface.blit(self.image, self.rect)

                self.text_color = 'white'
        
    def display_text_or_image(self):
        if '/' in self.content or "\\" in self.content:
            # Image
            image = pygame.image.load(self.content).convert_alpha()
            image_rect = image.get_rect(center=self.rect.center)
            self.display_surface.blit(image, image_rect)
        else:
            # Text
            font = pygame.font.Font(UI_FONT, BUTTON_FONT_SIZE)
            text_surf = font.render(self.content, False, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            self.display_surface.blit(text_surf, text_rect)

    def display(self):
        if self.rect_alignement == 'midtop': self.rect = self.image.get_rect(midtop=self.pos)
        elif self.rect_alignement == 'topleft': self.rect = self.image.get_rect(topleft=self.pos)
        
        self.check_hover_click()
        self.display_text_or_image()


class Text:
    def __init__(self, alignement, text, pos=None, font=UI_FONT, font_size=UI_FONT_SIZE, color='white'):
        self.alignement = alignement
        self.text = text
        self.pos = (SCREEN_WIDTH/2, 0) if pos is None else pos

        self.display_surface = pygame.display.get_surface()

        # Text
        self.font = pygame.font.Font(font, font_size)
        self.text_surf = self.font.render(str(text), False, color)
        if self.alignement == 'midtop': self.rect = self.text_surf.get_rect(midtop=self.pos)
        else: self.rect = self.text_surf.get_rect(topleft=self.pos)
        self.size = (font_size, font_size)

    def display(self):
        if self.alignement == 'midtop': self.rect = self.text_surf.get_rect(midtop=self.pos)
        else: self.rect = self.text_surf.get_rect(topleft=self.pos)
        
        self.display_surface.blit(self.text_surf, self.rect)
