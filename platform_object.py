import math

import pygame.draw

from constants import *


class PlatformObject:

    def __init__(self, frame, x, y, w=TILE_WIDTH, h=TILE_WIDTH, r=None, solid=True):
        self.frame = frame
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.r = r if r else w/2
        self.solid = solid
        self.vx = 0
        self.vy = 0
        self.ballistic = True

    def update(self, dt, events):
        """ Update physics """
        if self.ballistic:
            self.ballistic_update(dt)
        else:
            self.grounded_update(dt)
        if self.solid:
            self.collision_update()

    def draw(self, surface, offset):
        """ Render placeholder graphics """
        if self.ballistic:
            pygame.draw.circle(surface, (255, 0, 0), (self.x + offset[0], self.y + offset[1]), self.r, 2)
        else:
            pygame.draw.rect(surface, (255, 0, 0), self.get_rect(offset), 2)

    def ballistic_update(self, dt):
        """ Update velocity and position via continuous physics """
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx += (-DRAG * self.vx) * dt
        self.vy += (-DRAG * self.vy + GRAVITY) * dt

    def grounded_update(self, dt):
        """ Update velocity and position via continuous physics """
        self.x += self.vx * dt
        self.y += self.vy * dt
        if abs(self.vx) < V_MIN_SLIDE:
            self.vx = 0
        self.vx -= FRICTION * self.vx * dt

    def collision_update(self):
        """ Collide with any intersecting tiles and determine if object is grounded """
        tiles = self.frame.grid.get_nearby_tile_rects((self.x, self.y), *self.get_tile_range())
        ballistic = True
        for tile in tiles:
            # Check for tile collision
            d = self.collide(tile)
            if d:
                # Correct penetration
                self.x -= d[0]
                self.y -= d[1]
                # Reflect velocity along contact normal
                norm = math.sqrt(d[0] ** 2 + d[1] ** 2)
                if norm:
                    dv = d[0]/norm * self.vx + d[1]/norm * self.vy
                    if dv >= 0:
                        self.vx -= d[0] / norm * dv
                        self.vy -= d[1] / norm * dv
                        self.vx *= TANGENTIAL_RESITUTION
                        self.vy *= TANGENTIAL_RESITUTION
                        self.vx -= d[0] / norm * dv * RESTITUTION
                        self.vy -= d[1] / norm * dv * RESTITUTION
                # Check if grounded
                if self.ballistic and d[1] > 0 and (self.vy ** 2 + self.vx ** 2) < V_MIN_BOUNCE ** 2:
                    # Collided from above, with resulting velocity below a threshold
                    ballistic = False
                    self.vx = 0
                    self.vy = 0
                if not self.ballistic and self.y + self.h/2 <= tile.top:
                    # Still in contact with a tile directly below
                    ballistic = False
                # Custom behavior depending on tile type
                tile_type = self.frame.grid.get_tile_at(tile.center)
                self.on_collision(tile_type=tile_type, tile_rect=tile)
        self.set_ballistic(ballistic)

    def set_ballistic(self, new_val):
        if new_val == self.ballistic:
            return
        self.ballistic = new_val
        if new_val == True:
            self.on_become_ballistic()
        else:
            self.on_become_grounded()

    def on_become_ballistic(self):
        pass

    def on_become_grounded(self):
        pass

    def on_collision(self, tile_type, tile_rect):
        """ Override for any custom tile collision behavior """
        pass

    def get_tile_range(self):
        """ Minimum x and y distance of tiles to check for possible collisions """
        return (self.r, self.r) if self.ballistic else (self.w/2, self.h/2)

    def get_rect(self, offset=(0, 0)):
        """ Pygame rect for bounding box """
        dx, dy = self.get_tile_range()
        return pygame.Rect(self.x - dx + offset[0], self.y - dy + offset[1], 2 * dx, 2 * dy)

    def collide(self, rect):
        """ Automatically choose the correct collision function """
        if self.ballistic:
            return self.collide_circle(rect)
        else:
            return self.collide_box(rect)

    def collide_circle(self, rect):
        """ Return penetration vector from self to rect if collision occurs, else None """
        px = max(rect.left, min(rect.right, self.x))
        py = max(rect.top, min(rect.bottom, self.y))
        d = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        if d <= self.r:
            if d == 0:
                return 0, self.r
            scale = (d - self.r) / d
            return (self.x - px) * scale, (self.y - py) * scale
        else:
            return None

    def collide_box(self, rect):
        """ Return penetration vector from self to rect if collision occurs, else None """
        left, right = self.x - self.w/2, self.x + self.w/2
        top, bottom = self.y - self.h/2, self.y + self.h/2
        dx1 = right - rect.left
        dx2 = rect.right - left
        dy1 = bottom - rect.top
        dy2 = rect.bottom - top
        if max(dx1, dx2, dy1, dy2) < 0:
            return None
        dx = dx1 if dx1 < dx2 else -dx2
        dy = dy1 if dy1 < dy2 else -dy2
        if min(dx1, dx2) < min(dy1, dy2):
            return dx, 0
        else:
            return 0, dy

    def dist(self, pos):
        dx = pos.x - self.x
        dy = pos.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
