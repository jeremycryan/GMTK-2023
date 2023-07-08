import random

from grid import Grid

class Frame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        self.grid = Grid()

    def update(self, dt, events):
        self.grid.update(dt, events)
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))
        self.grid.draw(surface, offset)

    def next_frame(self):
        return Frame(self.game)