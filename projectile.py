import math

import pygame.draw

from constants import *


class Projectile:
    def __init__(self, frame, x, y, angle, r=10, v=BULLET_SPEED, damage=1):
        self.frame = frame
        self.x = x
        self.y = y
        self.r = r
        self.vx = math.cos(angle) * v
        self.vy = math.sin(angle) * v
        self.damage = damage
        self.zombies_hit = set()
        self.hit = False
        self.explode_time = 0.05

    def update(self, dt, events):
        if self.hit:
            self.explode_time -= dt
            if self.explode_time <= 0:
                self.frame.projectiles.remove(self)
            return
        # Move
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Check for wall collision
        tiles = self.frame.grid.get_nearby_tile_rects((self.x, self.y), self.r, self.r)
        for tile in tiles:
            d = self.collide(tile)
            if d:
                self.hit = True
        # Check for zombie collision
        for zombie in self.frame.zombies:
            if zombie in self.zombies_hit:
                continue
            if self.collide_zombie(zombie):
                zombie.vx += self.vx * BULLET_FORCE
                if zombie.ballistic:
                    zombie.vy += self.vy * BULLET_FORCE
                zombie.hit(self.damage)
                self.zombies_hit.add(zombie)
                if len(self.zombies_hit) >= self.frame.game.upgrade_levels[PIERCE] + 1:
                    self.hit = True

    def draw(self, surface, offset):
        if self.hit:
            pygame.draw.circle(surface, (255, 100, 0), (self.x + offset[0], self.y + offset[1]), self.r * 2)
        else:
            pygame.draw.circle(surface, (50, 50, 50), (self.x + offset[0], self.y + offset[1]), self.r)

    def collide(self, rect):
        """ Return true if collision occurs, else False """
        px = max(rect.left, min(rect.right, self.x))
        py = max(rect.top, min(rect.bottom, self.y))
        d = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        return d <= self.r

    def collide_zombie(self, zombie):
        dx = zombie.x - self.x
        dy = zombie.y - self.y
        if zombie.ballistic:
            return math.sqrt(dx ** 2 + dy ** 2) < zombie.r + self.r
        else:
            rx, ry = zombie.get_tile_range()
            return abs(dx) - rx - self.r < 0 and abs(dy) - rx - self.r < 0
