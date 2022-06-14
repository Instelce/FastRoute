import pygame

from settings import *


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


class Button:
    def __init__(self, content, callback=None, pos=None, rect_alignement='midtop', default_image="graphics/ui/buttons/default/default.png", hover_image="graphics/ui/buttons/default/hover.png") -> None:
        self.content = content
        self.callback = callback
        self.pos = (SCREEN_WIDTH/2, 200) if pos is None else pos
        self.rect_alignement = rect_alignement

        self.display_surface = pygame.display.get_surface()
        self.click = False

        # Image
        self.default_image = default_image
        self.hover_image = hover_image
        self.image = pygame.image.load(self.default_image).convert_alpha()
        self.size = self.image.get_size()

        # Text
        self.text_color = 'white'

    def check_hover_click(self):
        mouse_pos = pygame.mouse.get_pos()

        # Hover
        if self.rect.collidepoint(mouse_pos):
            self.image = pygame.image.load(self.hover_image).convert_alpha()
            self.display_surface.blit(self.image, self.rect)
            
            self.text_color = 'white'

            # Click
            if pygame.mouse.get_pressed()[0]:
                self.click = True
                if self.callback != None:
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
