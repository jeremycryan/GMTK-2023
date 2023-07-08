import random

import pygame

from grid import Grid, Tile
from hero import Hero
from zombie import Zombie


class Frame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        self.grid = Grid()
        self.zombies = []
        self.heros = [Hero(self, 900, 450)]

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(event.pos)
                self.zombies.append(Zombie(self, *event.pos))
        self.grid.update(dt, events)
        for hero in self.heros:
            hero.update(dt, events)
        for zombie in self.zombies:
            zombie.update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))
        self.grid.draw(surface, offset, only=[Tile.AIR])
        for hero in self.heros:
            hero.draw(surface, offset)
        for zombie in self.zombies:
            zombie.draw(surface, offset)
        self.grid.draw(surface, offset, only=[Tile.GROUND])

    def next_frame(self):
        return Frame(self.game)
