from random import randint
import pygame
from camera import Camera
from debug import debug
from player import Player
from enemy import Enemy
from supports import *
from tiles import *
from settings import *
from particle import Particle


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
        self.enemy_sprites = pygame.sprite.Group()
        self.light_sprites = pygame.sprite.Group()
        self.map_loader_sprites = pygame.sprite.Group()

        # Level
        self.level_index = level_index
        self.level_data = read_json_file(
            'data/levels.json')[str(self.level_index)]
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

        # Paticles
        self.particles = []

        # Create map
        self.create_map()

    def create_map(self):
        graphics = {
            'terrain': import_cut_graphics(r'graphics/terrain/tiles.png'),
            'spikes': import_cut_graphics(r'graphics/spikes/spikes_spawn.png'),
        }

        for style, layout in self.map_layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILE_SIZE
                        y = row_index * TILE_SIZE

                        surf = graphics['terrain'][int(col)]

                        if style == 'spawns':
                            if col == '0':  # Player
                                self.player = Player(
                                    (x, y), [self.visible_sprites], self.obstacle_sprites, self.camera)
                            if col == '1':  # Sniper Enemy
                                Enemy('sniper', (x, y), [
                                      self.visible_sprites, self.enemy_sprites])
                            if col == '2':  # Sniper Enemy
                                Enemy('pusher', (x, y), [
                                      self.visible_sprites, self.enemy_sprites])
                            if col == '4':  # Light
                                AnimatedTile('light', (x, y), [
                                             self.visible_sprites, self.light_sprites], 'graphics/light')
                            if col == '6':  # Portal
                                self.portal = AnimatedTile(
                                    'portal', (x, y), [self.visible_sprites], 'graphics/portal')
                        # Spikes
                        if style == 'spikes':
                            if col == '7':  # Circular 1
                                spike_surf = pygame.image.load(
                                    'graphics/spikes/circular/1.png').convert_alpha()
                                CircularSpike('circular_spikes', (x, y), [
                                              self.visible_sprites, self.spike_sprites], spike_surf)
                            if col == '15':  # Circular 2
                                spike_surf = pygame.image.load(
                                    'graphics/spikes/circular/2.png').convert_alpha()
                                CircularSpike('circular_spikes', (x, y), [
                                              self.visible_sprites, self.spike_sprites], spike_surf)
                            # Small spikes
                            if col == '1':
                                AnimatedTile('spikes', (x, y), [
                                    self.visible_sprites, self.spike_sprites], 'graphics/spikes/linear/small/up')
                            if col == '17':
                                AnimatedTile('spikes', (x, y), [
                                    self.visible_sprites, self.spike_sprites], 'graphics/spikes/linear/small/down')
                            if col == '8':
                                AnimatedTile('spikes', (x, y), [
                                    self.visible_sprites, self.spike_sprites], 'graphics/spikes/linear/small/left')
                            if col == '10':
                                AnimatedTile('spikes', (x, y), [
                                    self.visible_sprites, self.spike_sprites], 'graphics/spikes/linear/small/right')
                            # Large spikes
                            if col == '4':
                                LargeSpike('spikes', (x, y), [
                                    self.visible_sprites, self.spike_sprites], 'graphics/spikes/linear/large/up', 'up')
                            if col == '20':
                                LargeSpike('spikes', (x, y), [
                                    self.visible_sprites, self.spike_sprites], 'graphics/spikes/linear/large/down', 'down')
                            if col == '11':
                                LargeSpike('spikes', (x, y), [
                                    self.visible_sprites, self.spike_sprites], 'graphics/spikes/linear/large/left', 'left')
                            if col == '13':
                                LargeSpike('spikes', (x, y), [
                                    self.visible_sprites, self.spike_sprites], 'graphics/spikes/linear/large/right', 'right')

                            # Square spike
                            if col == '14':
                                spike_surf = pygame.image.load(
                                    'graphics/spikes/square/1.png').convert_alpha()
                                SquareSpike('spikes', (x, y), [self.visible_sprites, self.spike_sprites],
                                            spike_surf, self.obstacle_sprites, 'vertical')
                            if col == '6':
                                spike_surf = pygame.image.load(
                                    'graphics/spikes/square/1.png').convert_alpha()
                                SquareSpike('spikes', (x, y), [self.visible_sprites, self.spike_sprites],
                                            spike_surf, self.obstacle_sprites, 'horizontal')
                        if style == 'props':
                            SurfTile('props', (x, y), [
                                     self.visible_sprites], surf)
                        if style == 'wall':
                            SurfTile('wall', (x, y), [
                                self.visible_sprites, self.obstacle_sprites], surf)
                        if style == 'ground':
                            SurfTile('ground', (x, y), [
                                self.visible_sprites], surf)

    def create_particles(self):
        # Lights
        for light in self.light_sprites:
            for part in range(1, 2):
                self.particles.append(
                    Particle(light.rect.midtop[0], light.rect.midtop[1], [randint(0, 20) / 10 - 1, -2], 'white', randint(2, 4), True))
        # PLayer
        if self.player.force > 0:
            for part in range(1, 5):
                if part % 2 == 0:
                    color = 'purple'
                else:
                    color = 'blue'
                self.particles.append(
                    Particle(self.player.rect.centerx, self.player.rect.centery, [randint(0, 20) / 10 - 1, self.player.direction.y], color, randint(2, 4)))
        # for part in range(1, 5):
        #     if part % 2 == 0:
        #         color = 'purple'
        #     else:
        #         color = 'blue'
        #     self.particles.append(
        #         Particle(self.portal.rect.centerx, self.portal.rect.centery, [randint(0, 20) / 10 - 1, -2], color, randint(2, 4)))
        #     self.particles.append(
        #         Particle(self.portal.rect.centerx, self.portal.rect.centery, [randint(0, 20) / 10 - 1, -1], color, randint(2, 4)))

    def check_player_death(self):
        for spike_sprite in self.spike_sprites:
            if spike_sprite.rect.colliderect(self.player.rect):
                self.player_is_dead = True
            if spike_sprite.sprite_type == 'circular_spikes':
                if spike_sprite.death_box.colliderect(self.player.rect):
                    self.player_is_dead = True
            else:
                if spike_sprite.rect.colliderect(self.player.rect):
                    self.player_is_dead = True

    def check_level_is_done(self):
        if self.player.rect.colliderect(self.portal.rect):
            self.is_done = True

    def redirect(self):
        if self.player_is_dead:
            self.create_game_over_menu()
        if self.is_done:
            levels_data = read_json_file('data/levels.json')
            if self.level_index + 1 < len(levels_data):
                levels_data[str(self.level_index + 1)]['unlocked'] = True
                write_json_file('data/levels.json', levels_data)
            self.create_level_chooser_menu()

    def display(self):
        self.create_particles()

        self.redirect()
        self.check_player_death()
        self.check_level_is_done()

        self.camera.update(self.player)

        self.visible_sprites.update()
        for sprite in self.visible_sprites:
            self.display_surface.blit(sprite.image, self.camera.apply(sprite))

        # Draw particles
        for i, part in sorted(enumerate(self.particles), reverse=True):
            part.move(self.particles)
            part.draw(self.display_surface)

        # Draw indicator of player
        self.player.draw_indicator()

        # Call enemy behaviour
        for enemy in self.enemy_sprites:
            enemy.behaviour(self.player, [self.visible_sprites], [
                            self.visible_sprites, self.spike_sprites])

        # Debug
        debug(self.player.direction)
        debug(self.player.force, 20)
        debug(self.player.is_colliding, 30)
        debug(self.player.is_aim, 40)
        debug(self.player.shoot_count, 50)
        debug(self.player.rect, 60)
        debug(self.camera.get_offset(), 70)
        debug(pygame.mouse.get_pos(), 80)
        debug(len(self.particles), 90)
