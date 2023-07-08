import random

import pygame

from grid import Grid, Tile
from hero import Hero
from toss_ui import TossUI
from zombie import Zombie


class Frame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        self.grid = Grid()
        self.zombies = []
        self.heros = [Hero(self, 900, 450)]
        self.projectiles = []
        self.toss_ui = TossUI(self)

    def update(self, dt, events):
        self.toss_ui.update(dt, events)
        dt = self.toss_ui.adjust_time(dt)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and len(self.zombies) < 3:
                self.zombies.append(Zombie(self, *event.pos))
        self.grid.update(dt, events)
        for hero in self.heros:
            hero.update(dt, events)
        grabbed = []
        for zombie in self.zombies[:]:
            if zombie.grabbed:
                self.zombies.remove(zombie)
                grabbed.append(zombie)
            zombie.update(dt, events)
        self.zombies += grabbed
        for projectile in self.projectiles[:]:
            projectile.update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))
        self.grid.draw(surface, offset, only=[Tile.AIR])
        for hero in self.heros:
            hero.draw(surface, offset)
        for zombie in self.zombies:
            zombie.draw(surface, offset)
        for projectile in self.projectiles:
            projectile.draw(surface, offset)
        self.grid.draw(surface, offset, only=[Tile.GROUND])
        self.toss_ui.draw(surface, offset)

    def next_frame(self):
        return Frame(self.game)
