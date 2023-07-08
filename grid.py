import pygame
import random
import constants as c
from image_manager import ImageManager

import math


class Grid:

    def __init__(self):
        self.x = 0
        self.y = 0

        self.tile_surfs = {
            Tile.AIR: ImageManager.load("assets/images/air.png"),
            Tile.GROUND: ImageManager.load("assets/images/ground.png"),
        }

        self.char_map = {
            ".": Tile.AIR,
            "X": Tile.GROUND,
        }

        for key in self.tile_surfs:
            self.tile_surfs[key] = pygame.transform.scale(self.tile_surfs[key], c.TILE_SIZE)
        self.load_tiles("assets/levels/level1.txt")
        self.load_tile_surface_array()
        self.center()

    def center(self):
        width = len(self.tiles[0]) * c.TILE_WIDTH
        height = len(self.tiles) * c.TILE_HEIGHT
        self.x = c.WINDOW_WIDTH//2 - width//2
        self.y = c.WINDOW_HEIGHT//2 - height//2

    def load_tiles(self, path):
        with open(path) as f:
            raw = f.readlines()
        raw = [row.strip() for row in raw]
        width = len(raw[0])
        height = len(raw)
        self.tiles = [[Tile.AIR for _ in range(width)] for _ in range(height)]
        for y, row in enumerate(self.tiles):
            for x, tile in enumerate(row):
                character = raw[y][x]
                self.tiles[y][x] = self.char_map[character]

    def load_tile_surface_array(self):
        tile_surf = ImageManager.load("assets/images/tileset temp 128x128 per tile.png")
        tile_width = 128
        tile_height = 128
        count_wide = math.ceil(tile_surf.get_width()/tile_width)
        count_high = math.ceil(tile_surf.get_height()/tile_height)
        surfs = {}
        x = 0
        while x < count_wide:
            y = 0
            while y < count_high:
                minx = x*tile_width
                maxx = (x+1)*tile_width
                miny = y*tile_height
                maxy = (y+1)*tile_height
                new_surf = pygame.Surface((tile_width, tile_height), flags=pygame.SRCALPHA)
                new_surf.fill((255, 0, 0, 0))
                new_surf.blit(tile_surf, (-minx, -miny))
                new_surf = pygame.transform.scale(new_surf, c.TILE_SIZE)
                surfs[(x, y)] = new_surf
                y += 1
            x += 1
        self.tile_surface_array = surfs

    def get_tile_at(self, pos):
        """
        Gets tile at a particular world position
        """
        tpos = self.world_to_tile(pos)
        return self.get_tile_at_tile(tpos)

    def get_tile_at_tile(self, tpos):
        if tpos[0] < 0 or tpos[0] >= len(self.tiles[0]) or tpos[1] < 0 or tpos[1] >= len(self.tiles):
            return Tile.GROUND
        return self.tiles[math.floor(tpos[1])][math.floor(tpos[0])]

    def tile_is_solid(self, tile_enum):
        if tile_enum == Tile.AIR:
            return False
        return True

    def get_nearby_tile_rects(self, pos, x_dist, y_dist, only_solid=True):
        x_dist /= c.TILE_WIDTH
        y_dist /= c.TILE_HEIGHT
        tpos = self.world_to_tile(pos)
        min_tx = math.floor(tpos[0] - x_dist)
        max_tx = math.floor(tpos[0] + x_dist)
        min_ty = math.floor(tpos[1] - y_dist)
        max_ty = math.floor(tpos[1] + y_dist)
        tx = min_tx
        rects = []
        while tx <= max_tx:
            ty = min_ty
            while ty <= max_ty:
                if only_solid and not self.tile_is_solid(self.get_tile_at_tile((tx, ty))):
                    ty += 1
                    continue
                x, y = self.tile_to_world((tx, ty))
                width, height = c.TILE_WIDTH, c.TILE_HEIGHT
                rects.append(pygame.Rect(x, y, width, height))
                ty += 1
            tx += 1
        return rects

    def world_to_tile(self, pos):
        x, y = pos
        x -= self.x
        y -= self.y
        return x/c.TILE_WIDTH, y/c.TILE_HEIGHT

    def get_solid_neighbors(self, tx, ty):
        coords = []
        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                if x + tx < 0 or y + ty < 0 or x + tx >= len(self.tiles[0]) or y + ty >= len(self.tiles):
                    coords.append((x, y))
                    continue
                if self.tile_is_solid(self.tiles[ty+y][tx+x]):
                    coords.append((x, y))
                    continue
                # not solid
        return coords

    def tile_to_surf(self, tx, ty):
        neighbors = self.get_solid_neighbors(tx, ty)
        solid = c.SELF in neighbors
        if not solid:
            return self.tile_surfs[Tile.AIR]
        sheet_coord = (1, 1)
        if c.RIGHT in neighbors and c.DOWN in neighbors and c.LEFT not in neighbors and c.UP not in neighbors:
            sheet_coord = (0, 0)
        elif c.LEFT in neighbors and c.RIGHT in neighbors and c.DOWN in neighbors and c.UP not in neighbors:
            sheet_coord = (1, 0)
        elif c.LEFT in neighbors and c.DOWN in neighbors and c.UP not in neighbors and c.RIGHT not in neighbors:
            sheet_coord = (2, 0)
        elif c.LEFT not in neighbors and c.UP in neighbors and c.DOWN in neighbors and c.RIGHT in neighbors:
            sheet_coord = (0, 1)
        elif c.LEFT in neighbors and c.RIGHT not in neighbors and c.UP in neighbors and c.DOWN in neighbors:
            sheet_coord = (2, 1)
        elif c.LEFT not in neighbors and c.RIGHT in neighbors and c.UP in neighbors and c.DOWN not in neighbors:
            sheet_coord = (0, 2)
        elif c.LEFT in neighbors and c.RIGHT in neighbors and c.UP in neighbors and c.DOWN not in neighbors:
            sheet_coord = (1, 2)
        elif c.LEFT in neighbors and c.RIGHT not in neighbors and c.UP in neighbors and c.DOWN not in neighbors:
            sheet_coord = (2, 2)
        elif c.LEFT not in neighbors and c.RIGHT not in neighbors and c.DOWN not in neighbors and c.UP in neighbors:
            sheet_coord = (0, 3)
        elif c.LEFT in neighbors and c.RIGHT not in neighbors and c.UP not in neighbors and c.DOWN not in neighbors:
            sheet_coord = (1, 3)
        elif c.LEFT not in neighbors and c.RIGHT not in neighbors and c.DOWN in neighbors and c.UP not in neighbors:
            sheet_coord = (2, 3)
        elif c.LEFT not in neighbors and c.RIGHT not in neighbors and c.UP not in neighbors and c.DOWN not in neighbors:
            sheet_coord = (3, 0)
        elif c.LEFT in neighbors and c.RIGHT in neighbors and c.UP not in neighbors and c.DOWN not in neighbors:
            sheet_coord = (3, 1)
        elif c.LEFT not in neighbors and c.RIGHT not in neighbors and c.UP in neighbors and c.DOWN in neighbors:
            sheet_coord = (3, 2)
        elif c.LEFT not in neighbors and c.RIGHT in neighbors and c.UP not in neighbors and c.DOWN not in neighbors:
            sheet_coord = (3, 3)
        elif c.LEFT in neighbors and c.RIGHT in neighbors and c.UP in neighbors and c.DOWN in neighbors:
            # blank or internal corner
            if c.UP_RIGHT not in neighbors:
                sheet_coord = (4, 0)
            elif c.UP_LEFT not in neighbors:
                sheet_coord = (4, 1)
            elif c.DOWN_LEFT not in neighbors:
                sheet_coord = (4, 2)
            elif c.DOWN_RIGHT not in neighbors:
                sheet_coord = (4, 3)
            else:
                sheet_coord = (1, 1)
        return self.tile_surface_array[sheet_coord]


    def tile_to_world(self, pos):
        x, y = pos
        return x*c.TILE_WIDTH + self.x, y*c.TILE_HEIGHT + self.y

    def snap_up(self, pos):
        """
        Snaps a world position to the top left corner of that tile
        """
        tpos = self.world_to_tile(pos)
        stpos = math.floor(tpos[0]), math.floor(tpos[1])
        return self.tile_to_world(stpos)

    def update(self, dt, events):
        pass

    def draw(self, dest, offset=(0, 0), only=None):
        px = 0  # probe spots on the screen for what tile should display
        while px <= c.WINDOW_WIDTH + c.TILE_WIDTH:
            py = 0
            while py <= c.WINDOW_HEIGHT + c.TILE_HEIGHT:
                wx = px - offset[0]  # world position; where probe is relative to grid origin
                wy = py - offset[1]
                tile_pos = self.world_to_tile((wx, wy))
                tile_pos = math.floor(tile_pos[0]), math.floor(tile_pos[1])
                tile_type = Tile.GROUND
                if tile_pos[0] >= 0 and tile_pos[0] < len(self.tiles[0]):
                    if tile_pos[1] >= 0 and tile_pos[1] < len(self.tiles):
                        tile_type = self.tiles[tile_pos[1]][tile_pos[0]]
                if Tile.AIR in only:
                    tile_type = Tile.AIR # Don't worry about this
                if only is not None and tile_type not in only:
                    py += c.TILE_HEIGHT
                    continue

                if tile_type == Tile.AIR:
                    py += c.TILE_HEIGHT
                    continue
                tile_sprite = self.tile_to_surf(*tile_pos) if Tile.AIR not in only else self.tile_surfs[Tile.AIR]
                dest.blit(tile_sprite, self.snap_up((px, py)))
                py += c.TILE_HEIGHT
            px += c.TILE_WIDTH
        pass


class Tile:
    AIR=0
    GROUND=1
