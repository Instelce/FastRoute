import pygame
from debug import debug
from player import Player

from supports import *
from tiles import Tile
from settings import *


class Level:
    def __init__(self) -> None:
        
        # Setup
        self.display_surface = pygame.display.get_surface()

        # Groups
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

        self.create_map()

    def create_map(self):
        layouts = {
            'ground': import_csv_layout(r'maps\start\start_ground.csv'),
            'wall': import_csv_layout(r'maps\start\start_wall.csv'),
            'props': import_csv_layout(r'maps\start\start_props.csv'),
            'spawns': import_csv_layout(r'maps\start\start_spawns.csv'),
        }

        graphics = {
            'terrain': import_cut_graphics(r'graphics\terrain\tiles.png')
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE

                        surf = graphics['terrain'][int(col)]

                        if style == 'spawns':
                            if col == '0':
                                self.player = Player((x,y), [self.visible_sprites], self.obstacle_sprites)
                        if style == 'props':
                            Tile('props', (x,y), [self.visible_sprites], surf)
                        if style == 'wall':
                            Tile('wall', (x,y), [self.visible_sprites, self.obstacle_sprites], surf)
                        if style == 'ground':
                            Tile('ground', (x,y), [self.visible_sprites], surf)

    def display(self):
        self.visible_sprites.update()

        for sprite in self.visible_sprites:
            self.display_surface.blit(sprite.image, sprite.rect)

        # Debug
        debug(self.player.direction)
        debug(self.player.force, 20)
        debug(self.player.is_colliding, 30)
        debug(self.player.is_aim, 40)
        debug(self.player.shoot_count, 50)