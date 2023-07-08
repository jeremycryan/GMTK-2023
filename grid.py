import pygame
import random
import contants as c
from image_manager import ImageManager

class Grid:

    def __init__(self):
        self.x = 0
        self.y = 0

        self.tile_surfs = {
            Tile.AIR: ImageManager.load("assets/images/air.png"),
            Tile.GROUND: ImageManager.load("assets/images/ground.png"),
        }
        for key in self.tile_surfs:
            self.tile_surfs[key] = pygame.transform.scale(self.tile_surfs[key], c.TILE_SIZE)
        self.load_tiles()
        self.center()

    def center(self):
        width = len(self.tiles[0]) * c.TILE_WIDTH
        height = len(self.tiles) * c.TILE_HEIGHT
        self.x = c.WINDOW_WIDTH//2 - width//2
        self.y = c.WINDOW_HEIGHT//2 - height//2

    def load_tiles(self):
        width = 16
        height = 8
        self.tiles = [[random.choice((Tile.AIR, Tile.GROUND)) for _ in range(width)] for _ in range(height)]

    def world_to_tile(self, pos):
        x, y = pos
        x -= self.x
        y -= self.y
        return x/c.TILE_WIDTH, y/c.TILE_HEIGHT

    def tile_to_world(self, pos):
        x, y = pos
        return x*c.TILE_WIDTH + self.x, y*c.TILE_HEIGHT + self.y

    def snap_up(self, pos):
        """
        Snaps a world position to the top left corner of that tile
        """
        tpos = self.world_to_tile(pos)
        stpos = int(tpos[0]), int(tpos[1])
        return self.tile_to_world(stpos)

    def update(self, dt, events):
        pass

    def draw(self, dest, offset=(0, 0)):
        px = 0  # probe spots on the screen for what tile should display
        while px <= c.WINDOW_WIDTH + c.TILE_WIDTH:
            py = 0
            while py <= c.WINDOW_HEIGHT + c.TILE_HEIGHT:
                wx = px - offset[0]  # world position; where probe is relative to grid origin
                wy = py - offset[0]
                tile_pos = self.world_to_tile((wx, wy))
                tile_pos = int(tile_pos[0]), int(tile_pos[1])
                tile_type = Tile.GROUND
                if tile_pos[0] >= 0 and tile_pos[0] < len(self.tiles[0]):
                    if tile_pos[1] >= 0 and tile_pos[1] < len(self.tiles):
                        tile_type = self.tiles[tile_pos[1]][tile_pos[0]]

                tile_sprite = self.tile_surfs[tile_type] if tile_type in self.tile_surfs else Tile.GROUND
                dest.blit(tile_sprite, self.snap_up((px, py)))
                py += c.TILE_HEIGHT
            px += c.TILE_WIDTH


        pass


class Tile:
    AIR=0
    GROUND=1
