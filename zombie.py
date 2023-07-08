import math
import random

import pygame

from platform_object import PlatformObject
from constants import *

from image_manager import ImageManager
from pyracy.sprite_tools import Sprite, Animation


class Zombie(PlatformObject):
    IDLE = 0
    WALKING = 1
    BALLISTIC = 2


    def __init__(self, frame, x, y):
        super().__init__(frame, x, y, 30, 100, r=35)

        self.sprite = Sprite(12)
        self.state = Zombie.IDLE
        scale_by = 0.5
        fling = Animation(ImageManager.load("assets/images/zombie throw.png", scale_by=scale_by), (1, 1), 1)
        fling_right = Animation(ImageManager.load("assets/images/zombie throw.png", scale_by=scale_by), (1, 1), 1, reverse_x=True)
        idle = Animation(ImageManager.load("assets/images/zombie idle 256x256 12fps.png", scale_by=scale_by), (16, 1), 16)
        idle_right = Animation(ImageManager.load("assets/images/zombie idle 256x256 12fps.png", scale_by=scale_by), (16, 1), 16, reverse_x=True)
        hold = Animation(ImageManager.load("assets/images/zombie hold 256x256 12fps.png", scale_by=scale_by))
        hold_right = Animation(ImageManager.load("assets/images/zombie hold 256x256 12fps.png", scale_by=scale_by), reverse_x=True)
        self.sprite.add_animation(
            {
                "fling_left": fling,
                "fling_right": fling_right,
                "idle_left": idle,
                "idle_right": idle_right,
                "hold_left": hold,
                "hold_right": hold_right,
            },
            loop=True,
        )
        self.sprite.start_animation("idle_left")

        if self.ballistic:
            self.on_become_ballistic()



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
        self.sprite.update(dt, events)

    def draw(self, surface, offset):
        super().draw(surface, offset)
        my_surf = self.sprite.get_image()
        if self.state == Zombie.BALLISTIC:
            angle = math.atan2(-self.vy, self.vx) + math.pi
            my_surf = pygame.transform.rotate(my_surf, math.degrees(angle))
        x = self.x + offset[0] - my_surf.get_width()//2
        y = self.y + offset[1] - my_surf.get_height()//2
        surface.blit(my_surf, (x, y))

    def on_become_ballistic(self):
        super().on_become_ballistic()
        self.state = Zombie.BALLISTIC
        self.sprite.start_animation("fling_left")

    def on_become_grounded(self):
        super().on_become_grounded()
        self.state = Zombie.IDLE
        self.sprite.start_animation("idle_left")