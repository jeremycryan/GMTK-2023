import random

from platform_object import PlatformObject
from constants import *


class Zombie(PlatformObject):
    def __init__(self, frame, x, y):
        super().__init__(frame, x, y, 40, 40)

    def update(self, dt, events):
        """ Walk around randomly once zombie is grounded """
        super().update(dt, events)
        if not self.ballistic:
            if self.vx > 0:
                self.vx = ZOMBIE_SPEED
            elif self.vx < 0:
                self.vx = -ZOMBIE_SPEED
            else:
                self.vx = ZOMBIE_SPEED if random.random() > 0.5 else -ZOMBIE_SPEED
