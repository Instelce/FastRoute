from random import randint
import pygame
from sqlalchemy import true
from camera import Camera
from debug import debug
from player import Player

from supports import *
from tiles import MapLoaderRect, Spike, Tile
from settings import *


class Level:
    def __init__(self, level_index, create_level_chooser_menu, create_game_over_menu) -> None:
        
        # Setup
        self.display_surface = pygame.display.get_surface()
        self.create_level_chooser_menu = create_level_chooser_menu
        self.create_game_over_menu = create_game_over_menu

        # Groups
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.spike_sprites = pygame.sprite.Group()
        self.map_loader_sprites = pygame.sprite.Group()

        # Level
        self.level_index = level_index
        self.level_data = read_json_file('data/levels.json')[str(self.level_index)]
        self.is_done = False
        self.player_is_dead = False

        # Map 
        level_layouts = self.level_data['layouts']
        self.map_layouts = {}
        for style, layout in level_layouts.items():
            self.map_layouts[style] = import_csv_layout(layout)

        # Camera
        self.camera = Camera(
            len(self.map_layouts['wall'][0]) * TILE_SIZE, 
            len(self.map_layouts['wall']) * TILE_SIZE
        )

        # Create map
        self.create_map()

    def create_map(self):
        graphics = {
            'terrain': import_cut_graphics(r'graphics\terrain\tiles.png'),
            'spikes': import_cut_graphics(r'graphics\terrain\spikes.png'),
        }

        for style, layout in self.map_layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE

                        surf = graphics['terrain'][int(col)]
                        
                        if style == 'spawns':
                            if col == '0':
                                self.player = Player((x,y), [self.visible_sprites], self.obstacle_sprites, self.camera)
                            if col == '2':
                                portal_surf = pygame.image.load('graphics/portal/portal.png').convert_alpha()
                                self.portal = Tile('portal', (x,y), [self.visible_sprites], portal_surf)
                        if style == 'spikes':
                            spike_surf = graphics['spikes'][int(col)]
                            Spike('spikes', (x,y), [self.visible_sprites, self.spike_sprites], spike_surf)
                        if style == 'props':
                            Tile('props', (x,y), [self.visible_sprites], surf)
                        if style == 'wall':
                            Tile('wall', (x,y), [self.visible_sprites, self.obstacle_sprites], surf)
                        if style == 'ground':
                            Tile('ground', (x,y), [self.visible_sprites], surf)

    def check_player_death(self):
        for spike_sprite in self.spike_sprites:
            if spike_sprite.rect.colliderect(self.player.rect):
                self.player_is_dead = True
    
    def check_level_is_done(self):
        if self.player.rect.colliderect(self.portal.rect):
            self.is_done = True

    def redirect(self):
        if self.player_is_dead:
            self.create_game_over_menu()
        if self.is_done:
            if self.level_index + 1 < len(self.level_data):
                self.level_data[str(self.level_index+1)]['unlocked'] = True
                write_json_file('data/levels.json', self.level_data)
            self.create_level_chooser_menu()

    def display(self):
        self.redirect()
        self.check_player_death()
        self.check_level_is_done()

        self.camera.update(self.player)

        self.visible_sprites.update()
        for sprite in self.visible_sprites:
            self.display_surface.blit(sprite.image, self.camera.apply(sprite))
        
        self.player.draw_indicator()

        # Debug
        debug(self.player.direction)
        debug(self.player.force, 20)
        debug(self.player.is_colliding, 30)
        debug(self.player.is_aim, 40)
        debug(self.player.shoot_count, 50)
        debug(self.player.rect, 60)
        debug(self.camera.get_offset(), 70)
        debug(pygame.mouse.get_pos(), 80)
