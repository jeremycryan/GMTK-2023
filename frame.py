import random

import pygame

from grid import Grid
from zombie import Zombie


class Frame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        self.grid = Grid()
        self.zombies = []

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.zombies.append(Zombie(self, *event.pos))
        self.grid.update(dt, events)
        for zombie in self.zombies:
            zombie.update(dt, events)
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))
        self.grid.draw(surface, offset)
        for zombie in self.zombies:
            zombie.draw(surface, offset)

    def next_frame(self):
        return Frame(self.game)
