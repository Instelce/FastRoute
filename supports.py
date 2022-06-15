import pygame
from csv import reader
import json

from settings import *


def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map


def import_cut_graphics(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_num_x = int(surface.get_size()[0] / TILE_SIZE)
    tile_num_y = int(surface.get_size()[1] / TILE_SIZE)

    cut_tiles = []
    for row in range(tile_num_y):
        for col in range(tile_num_x):
            x = col * TILE_SIZE
            y = row * TILE_SIZE

            new_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
            new_surf.blit(surface, (0, 0), pygame.Rect(
                x, y, TILE_SIZE, TILE_SIZE))
            cut_tiles.append(new_surf)
    return cut_tiles


def read_json_file(path):
    with open(path, 'r') as f:
        cache = f.read()
        data = json.loads(cache)
    return data


def write_json_file(path, data):
    json_object = json.dumps(data, indent=4)
    with open(path, 'w') as f:
        f.write(json_object)
    return data