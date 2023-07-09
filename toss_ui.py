import math

import pygame
import constants as c
from image_manager import ImageManager


class TossUI:
    SLOWDOWN = 0.8
    FADE_IN_TIME = 0.25
    THROW_RADIUS = 100
    MAX_THROW_SPEED = 650

    def __init__(self, frame):
        self.frame = frame

        self.active = False
        self.activeness = 0

        self.shade = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill((0, 0, 0))
        self.shade.set_colorkey((255, 255, 255))
        self.shade.set_alpha(0)

        self.grabbed = None
        self.grab_point = None

        self.mpos = pygame.mouse.get_pos()
        self.mvel = (0, 0)
        self.grab_offset = (0, 0)
        self.throrrow = pygame.transform.rotate(ImageManager.load("assets/images/arrow.png", scale_by=0.5), -90)

    def hovered_zombie(self):
        hovered = None
        for zombie in self.frame.zombies[::-1]:
            x, y = pygame.mouse.get_pos()
            if zombie.collide(pygame.Rect(x, y, 1, 1)) and not zombie.ballistic:
                hovered = zombie
                break
        return hovered

    def draw(self, dest, offset=(0, 0)):
        if self.activeness == 0:
            return
        if self.grab_point:
            r = TossUI.THROW_RADIUS
            x = self.grab_point[0] - r
            y = self.grab_point[1] - r
            w = r
            #pygame.draw.circle(self.shade, (255, 255, 255), self.grab_point, w)
        self.shade.set_alpha(self.activeness*80)
        dest.blit(self.shade, (0, 0))
        if self.grab_point:
            pass
            #pygame.draw.circle(self.shade, (0, 0, 0), self.grab_point, w)
        if self.grabbed:
            self.grab_offset = self.mpos[0] - self.grabbed.x, self.mpos[1] - self.grabbed.y
            throw_strength = self.grab_offset_to_throw_strength(self.grab_offset)
            xoff = throw_strength[0] /15
            yoff = throw_strength[1] /15
            angle = math.atan2(-yoff, xoff)
            mag = math.sqrt(throw_strength[0]**2 + throw_strength[1]**2)
            scale = mag/TossUI.MAX_THROW_SPEED
            surf = pygame.transform.scale(self.throrrow, (self.throrrow.get_width()*scale, self.throrrow.get_height()*scale))
            surf = pygame.transform.rotate(surf, (angle*180/math.pi))
            x = self.grabbed.x + xoff - surf.get_width()//2 + math.cos(angle)*25
            y = self.grabbed.y + yoff - surf.get_height()//2 - math.sin(angle)*25
            dest.blit(surf, (x, y))
            self.grabbed.draw(dest, offset)

    def grab_offset_to_throw_strength(self, offset):
        x = offset[0]
        y = offset[1]
        x *= 10
        y *= 10
        mag = math.sqrt(x**2 + y**2)
        max_mag = TossUI.MAX_THROW_SPEED
        if mag > max_mag:
            x *= max_mag/mag
            y *= max_mag/mag
        return x, y


    def adjust_time(self, dt):
        dt *= (1 - self.active * TossUI.SLOWDOWN)
        return dt

    def update(self, dt, events):
        mpos = pygame.mouse.get_pos()
        self.mvel = mpos[0] - self.mpos[0], mpos[1] - self.mpos[1]
        self.mpos = mpos
        hovered = self.hovered_zombie()
        if hovered:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and hovered and not self.grabbed:
                self.grab_zombie(hovered)
            if event.type == pygame.MOUSEBUTTONUP:
                self.release_zombie()
                self.active = False

        if self.active:
            self.activeness += dt/TossUI.FADE_IN_TIME
            if self.activeness > 1:
                self.activeness = 1
            x, y = self.mpos
            if self.grab_point:
                dist = math.sqrt((x - self.grab_point[0])**2 + (y - self.grab_point[1])**2)
                # if dist > TossUI.THROW_RADIUS:
                #     self.release_zombie()
        else:
            self.activeness -= dt/TossUI.FADE_IN_TIME
            if self.activeness < 0:
                self.activeness = 0

        pass

    def grab_zombie(self, zombie):
        self.grabbed = zombie
        self.active = True
        self.grab_point = pygame.mouse.get_pos()
        zombie.grabbed = True

    def release_zombie(self):
        if self.grabbed:
            self.grabbed.grabbed = False
            self.grab_offset = self.mpos[0] - self.grabbed.x, self.mpos[1] - self.grabbed.y
            throw_strength = self.grab_offset_to_throw_strength(self.grab_offset)
            self.grabbed.vx = throw_strength[0]
            self.grabbed.vy = throw_strength[1]
            self.grabbed.on_become_ballistic()
            self.grabbed = None
        self.active = False