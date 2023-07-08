import math
import random

import pygame.draw

from constants import *
from image_manager import ImageManager
from platform_object import PlatformObject
from projectile import Projectile

from pyracy.sprite_tools import Sprite, Animation


class Hero(PlatformObject):

    def __init__(self, frame, x, y, w=100, h=100):
        super().__init__(frame, x, y, w, h)
        self.aim_angle = math.pi  # In radians!!!
        self.target_angle = self.aim_angle
        self.cooldown = HERO_COOLDOWN
        self.target = None
        self.t = 0
        self.hp = 5

        self.sprite = Sprite(12)
        idle = Animation(ImageManager.load("assets/images/Man Idle temp.png", 0.5), (1, 1), 1)
        idle_right = Animation(ImageManager.load("assets/images/Man Idle temp.png", 0.5), (1, 1), 1, reverse_x=True)
        self.sprite.add_animation({
            "idle_left":idle,
            "idle_right":idle_right,
        })
        self.sprite.start_animation("idle_left")

        self.arm_sprite = Sprite(12)
        aiming = Animation(ImageManager.load("assets/images/man arm aim temp.png", 0.5), (1, 1), 1)
        aiming_right = Animation(ImageManager.load("assets/images/man arm aim temp.png", 0.5), (1, 1), 1, reverse_x=True)
        standby = Animation(ImageManager.load("assets/images/man arm standby temp.png", 0.5), (1, 1), 1)
        standby_right = Animation(ImageManager.load("assets/images/man arm standby temp.png", 0.5), (1, 1), 1, reverse_x=True)
        self.arm_sprite.add_animation({
            "aiming_left": aiming,
            "aiming_right": aiming_right,
            "standby_left": standby,
            "standby_right": standby_right,
        })
        self.arm_sprite.start_animation("aiming_left")

    def facing_left(self):
        return (math.pi/2) < self.aim_angle%(2*math.pi) < (3*math.pi/2)

    def update(self, dt, events):
        super().update(dt, events)
        self.sprite.update(dt, events)
        self.arm_sprite.update(dt, events)
        self.t += dt
        # Remove if dead
        if self.hp <= 0:
            self.frame.heros.remove(self)
            # TODO: death animation
        # Select target
        self.target, self.target_angle = self.get_zombie()
        # Default to swivel aim if no target found
        if not self.target:
            if math.cos(self.aim_angle) > 0:
                self.target_angle = math.sin(self.t * 2) * 0.1
            else:
                self.target_angle = math.pi + math.sin(self.t * 2) * 0.1
            self.cooldown = HERO_COOLDOWN / 2
        # Face towards target
        if math.cos(self.aim_angle) * math.cos(self.target_angle) < 0:
            self.aim_angle = math.pi-self.aim_angle
        # Adjust aim towards target
        da = dt * SWIVEL_SPEED
        a1 = self.aim_angle + da
        a2 = self.aim_angle - da
        if abs((a1 - self.target_angle + math.pi) % (2*math.pi) - math.pi) < \
                abs((a2 - self.target_angle + math.pi) % (2*math.pi) - math.pi):
            self.aim_angle = a1
        else:
            self.aim_angle = a2
        if abs((self.aim_angle - self.target_angle + math.pi) % (2*math.pi) - math.pi) < da:
            self.aim_angle = self.target_angle
        # Shoot on a cooldown
        self.cooldown -= dt
        if self.cooldown <= 0 and self.target:
            self.cooldown = HERO_COOLDOWN
            self.shoot()

    def muzzle(self):
        """ Location of end of gun """
        x, y = self.muzzle_center()
        muzzle_length = 60
        x0 = x + muzzle_length*math.cos(self.aim_angle)
        y0 = y + muzzle_length*math.sin(self.aim_angle)
        return x0, y0

    def muzzle_center(self):
        """ Location of gun center of rotation (should be in line with the barrel)"""
        x_factor = -1 if self.facing_left() else 1
        return self.x + 30*x_factor, self.y + 10

    def gun_center(self):
        muz = self.muzzle()
        muz_rot = self.muzzle_center()
        length_down = 0.5
        return muz[0] * length_down + muz_rot[0] * (1-length_down), muz[1] * length_down + muz_rot[1] * (1 - length_down)

    def draw(self, surface, offset):
        super().draw(surface, offset)
        x, y = self.raycast(self.muzzle(), self.aim_angle)
        pygame.draw.line(surface, (255, 0, 0), (self.muzzle()), (x, y), 2)

        arm_surf = self.arm_sprite.get_image()
        if self.facing_left():
            arm_surf = pygame.transform.rotate(arm_surf, math.degrees(-self.aim_angle + math.pi) )
        x, y = self.gun_center()
        x -= arm_surf.get_width()//2
        y -= arm_surf.get_height()//2
        surface.blit(arm_surf, (x, y))

        self.sprite.x = self.x
        self.sprite.y = self.y
        self.sprite.draw(surface, offset)


    def raycast(self, origin, angle, step=1, max_length=1000):
        """ Find first collision of ray with the tilemap """
        x, y = origin
        for i in range(int(max_length/step)):
            px, py = x + i * step * math.cos(angle), y + i * step * math.sin(angle)
            if self.frame.grid.tile_is_solid(self.frame.grid.get_tile_at((px, py))):
                return px, py

    def shoot(self):
        """ Launch a projectile """
        self.vx -= math.cos(self.aim_angle) * RECOIL
        x, y = self.muzzle()
        dx, dy = math.sin(self.aim_angle), -math.cos(self.aim_angle)
        d = (random.random() - .5) * 2 * SHOT_JITTER
        self.frame.projectiles.append(Projectile(self.frame, x + dx * d, y + dy * d, self.aim_angle))

    def get_zombie(self, max_dist=1000):
        """ Get the closest zombie within line-of-sight, prioritizing previous target """
        x0, y0 = self.muzzle_center()
        min_dist = max_dist
        min_zombie = None
        for zombie in self.frame.zombies:
            true_dist = math.sqrt((zombie.x - x0) ** 2 + (zombie.y - y0) ** 2)
            dist = true_dist * TARGET_PRIORITY if zombie is self.target else true_dist
            # Check zombie is closer than any other zombies
            if dist < min_dist:
                x, y = self.raycast((x0, y0), math.atan2(zombie.y - y0, zombie.x - x0))
                # Check line of sight to zombie
                if math.sqrt((x - x0) ** 2 + (y - y0) ** 2) > true_dist:
                    min_zombie = zombie
                    min_dist = dist
        angle = math.atan2(min_zombie.y - y0, min_zombie.x - x0) if min_zombie else None
        return min_zombie, angle

    def hit(self, damage):
        self.hp -= damage
        # TODO: damage animation
