import math
import random

import pygame.draw

from constants import *
from grid import Tile
from platform_object import PlatformObject
from projectile import Projectile


class Hero(PlatformObject):

    def __init__(self, frame, x, y, w=64, h=100):
        super().__init__(frame, x, y, w, h)
        self.aim_angle = math.pi  # In radians!!!
        self.target_angle = self.aim_angle
        self.cooldown = HERO_COOLDOWN
        self.target = None
        self.t = 0
        self.hp = 5
        self.location = None
        self.destination = None

    def update(self, dt, events):
        super().update(dt, events)
        self.t += dt
        # Remove if dead
        if self.hp <= 0:
            self.frame.heros.remove(self)
            # TODO: death animation
        # Update navigation
        self.navigate()
        if self.destination:
            self.vx_des = math.copysign(HERO_SPEED, self.destination[0] - self.location[0])
            if not self.ballistic and self.destination[1] < self.location[1]:
                self.vy -= HERO_JUMP
        else:
            self.vx_des = 0
        if self.ballistic:
            self.vx = self.vx_des
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
        x0 = x + 20*math.cos(self.aim_angle)
        y0 = y + 20*math.sin(self.aim_angle)
        return x0, y0

    def muzzle_center(self):
        """ Location of gun center of rotation (should be in line with the barrel)"""
        return self.x, self.y

    def draw(self, surface, offset):
        pygame.draw.rect(surface, (255, 0, 0), self.get_rect(offset), 2)
        x, y = self.raycast(self.muzzle(), self.aim_angle)
        pygame.draw.line(surface, (255, 0, 0), (self.muzzle()), (x, y), 2)

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

    def navigate(self):
        if self.ballistic:
            return
        x, y = self.frame.grid.world_to_tile((self.x, self.y + self.h/2 + 1))
        x, y = math.floor(x), math.floor(y)
        # Left previous tile; choose a new goal
        if (x, y) != self.location or self.destination is None:
            self.location = (x, y)
            dx = 1 if (random.random() > 0.5) else -1
            for dy in range(-2, 3):
                tile0 = self.frame.grid.get_tile_at_tile((x + dx, y + dy))
                tile1 = self.frame.grid.get_tile_at_tile((x + dx, y + dy - 1))
                tile2 = self.frame.grid.get_tile_at_tile((x + dx, y + dy - 2))
                if tile0 == Tile.GROUND and tile1 == Tile.AIR and tile2 == Tile.AIR:
                    self.destination = (x + dx, y + dy)
                    self.vx = 0
                    return
            self.destination = None

    def collide(self, rect):
        return self.collide_box(rect)

    def get_tile_range(self):
        """ Minimum x and y distance of tiles to check for possible collisions """
        return self.w/2, self.h/2
