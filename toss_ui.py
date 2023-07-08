import math

import pygame
import constants as c

class TossUI:
    SLOWDOWN = 0.7
    FADE_IN_TIME = 0.25
    THROW_RADIUS = 100

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
            pygame.draw.circle(self.shade, (255, 255, 255), self.grab_point, w)
        self.shade.set_alpha(self.activeness*80)
        dest.blit(self.shade, (0, 0))
        if self.grab_point:
            pygame.draw.circle(self.shade, (0, 0, 0), self.grab_point, w)
        pass

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
                if dist > TossUI.THROW_RADIUS:
                    self.release_zombie()
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
            self.grabbed.vx = self.mvel[0]*7
            self.grabbed.vy = self.mvel[1]*7
            self.grabbed.on_become_ballistic()
            self.grabbed = None
        self.active = False