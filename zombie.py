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
    LANDING = 4

    def __init__(self, frame, x, y):
        super().__init__(frame, x, y, 52, 52, r=26)

        self.sprite = Sprite(12)
        self.state = Zombie.IDLE
        self.hp = 5
        self.death_time = 0.2
        self.grabbed = False
        self.cooldown = 0
        self.damage = 1

        scale_by = 0.5
        fling = Animation(ImageManager.load("assets/images/ZR Throw temp.png", scale_by=scale_by), (1, 1), 1)
        fling_right = Animation(ImageManager.load("assets/images/ZR Throw temp.png", scale_by=scale_by), (1, 1), 1, reverse_x=True)
        idle = Animation(ImageManager.load("assets/images/ZR Idle temp.png", scale_by=scale_by), (1, 1), 1)
        idle_right = Animation(ImageManager.load("assets/images/ZR Idle temp.png", scale_by=scale_by), (1, 1), 1, reverse_x=True)
        hold = Animation(ImageManager.load("assets/images/ZR held temp.png", scale_by=scale_by), (2, 1), 2)
        hold_right = Animation(ImageManager.load("assets/images/ZR held temp.png", scale_by=scale_by), (2, 1), 2, reverse_x=True)
        falling = Animation(ImageManager.load("assets/images/ZR Fall Temp.png", scale_by=scale_by), (1, 1), 1)
        falling_right = Animation(ImageManager.load("assets/images/ZR Fall Temp.png", scale_by=scale_by), (1, 1), 1, reverse_x=True)
        land = Animation(ImageManager.load("assets/images/ZR Land Temp.png", scale_by=scale_by), (1, 1), 1)
        land_right = Animation(ImageManager.load("assets/images/ZR Land Temp.png", scale_by=scale_by), (1, 1), 1, reverse_x=True)
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
                "land_left": land,
                "land_right": land_right,
            },
            loop=True,
        )
        self.sprite.chain_animation("land_left", "idle_left")
        self.sprite.chain_animation("land_right","idle_right")
        self.sprite.add_callback("land_left", self.on_land, [True])
        self.sprite.add_callback("land_right", self.on_land, [False])
        self.sprite.start_animation("idle_left")

        self.agape = False

        if self.ballistic:
            self.on_become_ballistic()

        self.squash = 1.0

    def update(self, dt, events):
        """ Walk around randomly once zombie is grounded """
        super().update(dt, events)
        if self.hp <= 0:
            self.grabbed = False
            self.death_time -= dt
            if self.death_time <= 0:
                self.frame.zombies.remove(self)
            return
        self.cooldown -= dt
        if self.cooldown <= 0:
            self.attack()
        if self.grabbed:
            self.state = Zombie.GRABBED
            self.ballistic = False
            self.vx = 0
            self.vy = 0
            #self.x, self.y = pygame.mouse.get_pos()

        if not self.ballistic and not self.grabbed and not self.state == Zombie.LANDING:
            if self.vx_des > 0:
                self.vx_des = ZOMBIE_SPEED
                self.sprite.start_animation("idle_right", restart_if_active=False)
            elif self.vx_des < 0:
                self.vx_des = -ZOMBIE_SPEED
                self.sprite.start_animation("idle_left", restart_if_active=False)
            else:
                self.vx_des = ZOMBIE_SPEED if random.random() > 0.5 else -ZOMBIE_SPEED
        self.sprite.update(dt, events)

        if self.state == Zombie.IDLE:
            ds = 1.0 - self.squash
            if ds:
                self.squash += ds*dt*15
            if abs(self.squash - 1) < 0.05:
                self.squash = 1

    def draw(self, surface, offset):
        super().draw(surface, offset)
        my_surf = self.sprite.get_image()
        direction = "left" if self.vx < 0 else "right"
        if self.death_time <= 0:
            pass  # TODO: death animation
        if self.state == Zombie.BALLISTIC and not self.grabbed:
            if self.vy < 0 and self.agape:
                self.sprite.start_animation(f"fling_{direction}", restart_if_active=False)
                angle = math.atan2(-self.vy, self.vx) + (math.pi if self.vx < 0 else 0)
                my_surf = pygame.transform.rotate(my_surf, math.degrees(angle))
            else:
                self.agape = False
                self.sprite.start_animation(f"falling_{direction}", restart_if_active=False)
                self.squash = max(1/(1 + abs(self.vy)*0.0005), 0.7)

        if self.grabbed:
            self.sprite.start_animation(f"hold_{direction}", restart_if_active=False)
        if self.squash != 1.0:
            my_surf = pygame.transform.scale(my_surf, (my_surf.get_width()*self.squash, my_surf.get_height()*(1/self.squash)))
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
        self.vx_des = math.copysign(ZOMBIE_SPEED, self.vx)

    def on_become_grounded(self):
        super().on_become_grounded()
        if self.grabbed:
            return
        direction = "left" if ("left" in self.sprite.active_animation_key) else "right"
        self.sprite.start_animation(f"land_{direction}")
        self.state = Zombie.LANDING

    def on_land(self, left=True):
        if left:
            self.sprite.start_animation(f"idle_left")
        else:
            self.sprite.start_animation(f"idle_right")
        self.squash = 1.3
        self.state = Zombie.IDLE

    def hit(self, damage):
        self.hp -= damage

    def on_collision(self, tile_type, tile_rect):
        dx, dy = self.get_tile_range()
        if tile_rect.top < self.y < tile_rect.bottom:
            if tile_rect.left >= self.x + dx and self.vx_des > 0:
                self.vx_des = -self.vx_des
            if tile_rect.right <= self.x - dx and self.vx_des < 0:
                self.vx_des = -self.vx_des

    def attack(self):
        for hero in self.frame.heros:
            if self.collide(hero.get_rect()):
                # TODO: attack animation
                hero.hit(self.damage)
                hero.vx += math.copysign(ZOMBIE_KNOCKBACK, self.vx_des)
                self.cooldown = ZOMBIE_COOLDOWN
                break
