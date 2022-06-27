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
from audio import audio_manager


class Level:
    def __init__(self, level_index, create_level_chooser_menu, create_game_over_menu, endless=None) -> None:

        # Setup
        self.display_surface = pygame.display.get_surface()
        self.create_level_chooser_menu = create_level_chooser_menu
        self.create_game_over_menu = create_game_over_menu

        # Endless
        self.is_endless = False if endless is None else endless

        # Groups
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        self.spike_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.light_sprites = pygame.sprite.Group()
        self.map_loader_sprites = pygame.sprite.Group()

        # Level
        self.is_done = False
        self.player_is_dead = False

        if not self.is_endless:
            self.level_index = level_index
            self.level_data = read_json_file(
                'data/levels.json')[str(self.level_index)]
            level_layouts = self.level_data['layouts']

        else:
            self.level_index = 0
            self.level_data = {
                "wall": "maps/endless/start/start_wall.csv",
                "spikes": "maps/endless/start/start_spikes.csv",
                "spawns": "maps/endless/start/start_spawns.csv"
            }
            level_layouts = self.level_data

        # Map
        self.map_layouts = {}
        for style, layout in level_layouts.items():
            self.map_layouts[style] = import_csv_layout(layout)

        # Camera
        self.LEVEL_WIDTH = len(self.map_layouts['wall'][0]) * TILE_SIZE
        self.LEVEL_HEIGHT = len(self.map_layouts['wall']) * TILE_SIZE
        self.camera = Camera(
            self.LEVEL_WIDTH,
            self.LEVEL_HEIGHT
        )
        self.camera_offset = self.camera.get_offset()

        # Paticles
        self.particles = []
        self.particles_time = pygame.time.get_ticks()

        # Create map
        self.create_map()

        # Rising spikes
        rising_spikes_surf = pygame.image.load(
            'graphics/spikes/rising_spikes.png').convert_alpha()
        self.rising_spikes = SurfTile('spikes', (0, self.LEVEL_HEIGHT), [
                                      self.visible_sprites, self.spike_sprites], rising_spikes_surf)
        self.rising_spikes_time = pygame.time.get_ticks()
        self.rising_spikes_can_move = False
        self.hide_rect = pygame.Rect(
            0, self.rising_spikes.rect.top + self.camera_offset[1], SCREEN_WIDTH, self.rising_spikes.rect.height)

        # Create background
        self.create_background()
        self.background_surface_angle = 0
        self.background_time = pygame.time.get_ticks()

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
                                      self.visible_sprites, self.enemy_sprites], self.camera)
                            if col == '2':  # Sniper Enemy
                                Enemy('pusher', (x, y), [
                                      self.visible_sprites, self.enemy_sprites], self.camera)
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

    def load_maps(self):
        # if self.LEVEL_HEIGHT // 2.5 < abs(self.camera_offset[1]) < self.LEVEL_HEIGHT - (self.LEVEL_HEIGHT // 2.5):
        #     print("LOAD NEW MAP", self.LEVEL_HEIGHT // 2.5,
        #           abs(self.camera_offset[1]), self.LEVEL_HEIGHT - (self.LEVEL_HEIGHT // 2.5))

        self.map_loader = pygame.Surface(
            (SCREEN_WIDTH, self.LEVEL_HEIGHT // 4))
        self.map_loader.fill('red')
        self.display_surface.blit(
            self.map_loader, (0, (self.LEVEL_HEIGHT // 2) + self.camera_offset[1] - self.map_loader.get_height() // 2))

    def rising_spikes_movement(self):
        current_time = pygame.time.get_ticks()

        if self.player.force > 0:
            self.rising_spikes_can_move = True

        if self.player.direction.y != 0 and not self.player.is_aim:
            move_cooldown = 100
        else:
            move_cooldown = 1000

        if self.rising_spikes_can_move and current_time - self.rising_spikes_time >= move_cooldown:
            self.rising_spikes_time = current_time
            self.rising_spikes.rect.y -= 16
            self.hide_rect.height += 16

        print(move_cooldown)

        self.hide_rect.top = self.rising_spikes.rect.top + \
            self.camera_offset[1] + (2 * TILE_SIZE)

    def create_particles(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.particles_time >= 100:
            self.particles_time = current_time
            # Lights
            for light in self.light_sprites:
                for part in range(1, 2):
                    if part % 2 == 0:
                        color = '#ffffff'
                    else:
                        color = 'yellow'
                    self.particles.append(
                        Particle(light.rect.midtop[0] + int(self.camera_offset[0]), light.rect.midtop[1] + int(self.camera_offset[1]), [randint(0, 20) / 10 - 1, -2], color, randint(2, 4), True))
        # PLayer
        if self.player.force > 0:
            for part in range(1, 2):
                if part % 2 == 0:
                    color = '#724cac'
                else:
                    color = '#9872b6'
                self.particles.append(
                    Particle(self.player.rect.centerx + self.camera_offset[0], self.player.rect.centery + self.camera_offset[1], [randint(0, 20) / 10 - 1, self.player.direction.y], color, randint(2, 4)))

    def create_background(self):
        self.background_rects = []
        for i in range(0, self.LEVEL_HEIGHT, 200):
            print(i, '/', self.LEVEL_HEIGHT)
            self.background_rects.append(
                [(0, i + self.camera_offset[1]),
                 pygame.Surface((SCREEN_WIDTH, 160), pygame.SRCALPHA)]
            )
        for surface in self.background_rects:
            surface[1].fill((10, 10, 10))

    def display_background(self):
        current_time = pygame.time.get_ticks()

        for surface in self.background_rects:
            # Update pos
            surface[0] = (
                surface[0][0], surface[0][1] + 1)

            # Reset pos
            if surface[0][1] > self.LEVEL_HEIGHT:
                surface[0] = (surface[0][0], -100)

            # Set angle
            if self.player.force > 0:
                if self.background_surface_angle < 10 and current_time - self.background_time >= 100:
                    self.background_time = current_time
                    self.background_surface_angle += self.player.force // 20
            else:
                if self.background_surface_angle > 0 and current_time - self.background_time >= 10:
                    self.background_time = current_time
                    self.background_surface_angle -= 1

            # Rotate and draw
            surface_rot = pygame.transform.rotate(
                surface[1], -self.background_surface_angle)
            self.display_surface.blit(surface_rot, surface[0])

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
        if not self.is_endless:
            if self.player.rect.colliderect(self.portal.rect):
                self.is_done = True

    def redirect(self):
        if self.player_is_dead:
            # audio_manager.play_sound('die')
            self.create_game_over_menu()
        if self.is_done:
            levels_data = read_json_file('data/levels.json')
            if self.level_index + 1 < len(levels_data):
                levels_data[str(self.level_index + 1)]['unlocked'] = True
                write_json_file('data/levels.json', levels_data)
            self.create_level_chooser_menu()

    def display(self):
        self.camera_offset = self.camera.get_offset()

        self.display_background()
        self.create_particles()

        if self.is_endless:
            self.load_maps()

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

        # Rising spikes
        self.rising_spikes_movement()
        pygame.draw.rect(self.display_surface, 'black', self.hide_rect)
        print(self.hide_rect.topleft, self.rising_spikes.rect.topleft)

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
