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
    GRABBED = 3


    def __init__(self, frame, x, y):
        super().__init__(frame, x, y, 64, 64, r=32)

        self.sprite = Sprite(12)
        self.state = Zombie.IDLE
        self.grabbed = False
        scale_by = 0.5
        fling = Animation(ImageManager.load("assets/images/ZR Throw temp.png", scale_by=scale_by), (1, 1), 1)
        fling_right = Animation(ImageManager.load("assets/images/ZR Throw temp.png", scale_by=scale_by), (1, 1), 1, reverse_x=True)
        idle = Animation(ImageManager.load("assets/images/ZR Idle temp.png", scale_by=scale_by), (1, 1), 1)
        idle_right = Animation(ImageManager.load("assets/images/ZR Idle temp.png", scale_by=scale_by), (1, 1), 1, reverse_x=True)
        hold = Animation(ImageManager.load("assets/images/ZR held temp.png", scale_by=scale_by), (2, 1), 2)
        hold_right = Animation(ImageManager.load("assets/images/ZR held temp.png", scale_by=scale_by), (2, 1), 2, reverse_x=True)
        falling = Animation(ImageManager.load("assets/images/ZR Fall Temp.png", scale_by=scale_by), (1, 1), 1)
        falling_right = Animation(ImageManager.load("assets/images/ZR Fall Temp.png", scale_by=scale_by), (1, 1), 1, reverse_x=True)
        self.sprite.add_animation(
            {
                "fling_left": fling,
                "fling_right": fling_right,
                "idle_left": idle,
                "idle_right": idle_right,
                "hold_left": hold,
                "hold_right": hold_right,
                "falling_left": falling,
                "falling_right": falling_right,
            },
            loop=True,
        )
        self.sprite.start_animation("idle_left")

        self.agape = False

        if self.ballistic:
            self.on_become_ballistic()



    def update(self, dt, events):
        """ Walk around randomly once zombie is grounded """
        super().update(dt, events)
        if self.grabbed:
            self.state = Zombie.GRABBED
            self.ballistic = False
            self.vx = 0
            self.vy = 0
            self.x, self.y = pygame.mouse.get_pos()

        if not self.ballistic and not self.grabbed:
            if self.vx > 0:
                self.vx = ZOMBIE_SPEED
                self.sprite.start_animation("idle_right", restart_if_active=False)
            elif self.vx < 0:
                self.vx = -ZOMBIE_SPEED
                self.sprite.start_animation("idle_left", restart_if_active=False)
            else:
                self.vx = ZOMBIE_SPEED if random.random() > 0.5 else -ZOMBIE_SPEED
        self.sprite.update(dt, events)

    def draw(self, surface, offset):
        super().draw(surface, offset)
        my_surf = self.sprite.get_image()
        direction = "left" if self.vx < 0 else "right"
        if self.state == Zombie.BALLISTIC and not self.grabbed:
            if self.vy < 0 and self.agape:
                self.sprite.start_animation(f"fling_{direction}", restart_if_active=False)
                angle = math.atan2(-self.vy, self.vx) + (math.pi if self.vx < 0 else 0)
                my_surf = pygame.transform.rotate(my_surf, math.degrees(angle))
            else:
                self.agape = False
                self.sprite.start_animation(f"falling_{direction}", restart_if_active=False)
        if self.grabbed:
            self.sprite.start_animation(f"hold_{direction}", restart_if_active=False)
        x = self.x + offset[0] - my_surf.get_width()//2
        y = self.y + offset[1] - my_surf.get_height()//2
        surface.blit(my_surf, (x, y))

    def on_become_ballistic(self):
        super().on_become_ballistic()
        if self.grabbed:
            return
        if self.vy < 0:
            self.agape = True
            self.sprite.start_animation("fling_left")
        else:
            self.sprite.start_animation("falling_left")
        self.state = Zombie.BALLISTIC


    def on_become_grounded(self):
        super().on_become_grounded()
        if self.grabbed:
            return
        self.state = Zombie.IDLE
