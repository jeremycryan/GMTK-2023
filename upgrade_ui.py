import random

import pygame
import constants as c
from image_manager import ImageManager


class UpgradeUI:
    FADE_IN_TIME = 0.25

    def __init__(self, frame):
        self.frame = frame

        self.active = False
        self.activeness = 0
        self.age = 0

        self.shade = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill((0, 0, 0))
        self.shade.set_colorkey((255, 255, 255))
        self.shade.set_alpha(0)
        self.over_shade = self.shade.copy()

        self.title_font = pygame.font.Font("assets/fonts/edge_of_the_galaxy.otf", 70)
        self.title_surf = self.title_font.render("Hero level up!", 1, (255, 255, 255))
        self.subtitle_font = pygame.font.Font("assets/fonts/segoeui.ttf", 22)
        self.subtitle_font_surfs = [
            self.subtitle_font.render("You've beaten him for now,", 1, (255, 255, 255)),
            self.subtitle_font.render("but he'll come back even stronger.", 1, (255, 255, 255)),
        ]

        self.hovered = None

        self.upgrade_surfs = []
        self.upgrade_name_font = pygame.font.Font("assets/fonts/edge_of_the_galaxy.otf", 27)
        self.upgrade_names = {name:[self.upgrade_name_font.render(line.upper(), 1, (255, 255, 255)) for line in c.UPGRADE_NAMES[name].split()] for name in c.UPGRADE_NAMES}
        self.upgrade_description_font = self.subtitle_font
        self.upgrade_descriptions = {name:[self.upgrade_description_font.render(line, 1, (255, 255, 255)) for line in c.UPGRADE_DESCRIPTIONS[name].split("\n")] for name in c.UPGRADE_NAMES}

        self.level_font = pygame.font.Font("assets/fonts/segoeui.ttf", 16)

    def raise_up(self):
        self.active = True
        self.upgrade_surfs = self.get_upgrade_surfs()

    def update(self, dt, events):
        self.age += dt
        if self.activeness == 0 and self.active == False and self.frame.complete == True:
            self.frame.done = True

        if self.active:
            self.activeness += dt/UpgradeUI.FADE_IN_TIME
            if self.activeness > 1:
                self.activeness = 1
        else:
            self.activeness -= dt/UpgradeUI.FADE_IN_TIME*0.6
            if self.activeness < 0:
                self.activeness = 0

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.active:
                    self.process_click()
                    events.remove(event)
            if event.type == pygame.MOUSEBUTTONUP:
                if self.active:
                    events.remove(event)
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_o:
            #         self.frame.complete = True
            #         self.raise_up()

        self.update_hover()

    def update_hover(self):
        mpos = pygame.mouse.get_pos()
        x = c.WINDOW_WIDTH//2
        y = c.WINDOW_HEIGHT//2 + 10
        self.hovered = None
        for key, up_surf in self.upgrade_surfs:
            rect = pygame.Rect(x - up_surf.get_width()//2, y - up_surf.get_height()//2, up_surf.get_width(), up_surf.get_height())
            if rect.collidepoint(*mpos):
                self.hovered = key
            y += up_surf.get_height() + 15

    def process_click(self):
        if not self.active:
            return
        mpos = pygame.mouse.get_pos()
        x = c.WINDOW_WIDTH//2
        y = c.WINDOW_HEIGHT//2 + 10
        for key, up_surf in self.upgrade_surfs:
            rect = pygame.Rect(x - up_surf.get_width()//2, y - up_surf.get_height()//2, up_surf.get_width(), up_surf.get_height())
            if rect.collidepoint(*mpos):
                self.select_upgrade(key)
            y += up_surf.get_height() + 15

    def select_upgrade(self, key):
        self.frame.game.upgrade_levels[key] += 1
        self.active = False

    def draw(self, surf, offset=(0, 0)):


        if (self.activeness <= 0 and not self.frame.complete) and self.age > UpgradeUI.FADE_IN_TIME:
            return

        self.shade.set_alpha(210*self.activeness)
        self.over_shade.set_alpha(0)
        if self.age < UpgradeUI.FADE_IN_TIME:
            self.over_shade.set_alpha(255 * (1 - self.age/self.FADE_IN_TIME))
            surf.blit(self.over_shade, (0, 0))
            return
        if self.active == False and self.frame.complete:
            self.shade.set_alpha(210)
            self.over_shade.set_alpha(255 * (1 - self.activeness))
        surf.blit(self.shade, (0, 0))

        x = c.WINDOW_WIDTH//2 - self.title_surf.get_width()//2
        y = c.WINDOW_HEIGHT//2 - self.title_surf.get_height()//2 - 185
        surf.blit(self.title_surf, (x, y))

        yoff = -25
        for line in self.subtitle_font_surfs:
            x = c.WINDOW_WIDTH//2 - line.get_width()//2
            y = c.WINDOW_HEIGHT//2 - line.get_height()//2 - 100 + yoff
            surf.blit(line, (x, y))
            yoff += 27

        x = c.WINDOW_WIDTH//2
        y = c.WINDOW_HEIGHT//2 + 10
        for key, up_surf in self.upgrade_surfs:
            if key == self.hovered:
                up_surf.set_alpha(255)
            else:
                up_surf.set_alpha(128)
            surf.blit(up_surf, (x - up_surf.get_width()//2, y - up_surf.get_height()//2))
            y += up_surf.get_height() + 15

        if self.over_shade.get_alpha() > 0:
            surf.blit(self.over_shade, (0, 0))

    def get_upgrade_surfs(self):
        surfs = []
        possible_upgrades = list(c.UPGRADE_NAMES)
        if self.frame.game.upgrade_levels[c.WALK_SPEED] >= 2:
            possible_upgrades.remove(c.WALK_SPEED)
        if self.frame.game.upgrade_levels[c.ACCURACY] >= 2:
            possible_upgrades.remove(c.ACCURACY)
        if self.frame.game.upgrade_levels[c.PIERCE] >= 3:
            possible_upgrades.remove(c.PIERCE)
        if self.frame.game.upgrade_levels[c.LEFTY] >= 1:
            possible_upgrades.remove(c.LEFTY)
        for i in range(3):
            if not possible_upgrades:
                continue
            upgrade = random.choice(possible_upgrades)
            possible_upgrades.remove(upgrade)
            surf = ImageManager.load_copy("assets/images/upgrade_outline.png")
            surf.set_colorkey((0, 0, 0))

            name_lines = self.upgrade_names[upgrade]

            height = sum([surf.get_height() for surf in name_lines]) + 5*(len(name_lines)-1)
            y = surf.get_height()//2 - height//2 + 2
            for line in name_lines:
                x = 170 - line.get_width()
                surf.blit(line, (x, y))
                y += line.get_height()+5

            descriptions = self.upgrade_descriptions[upgrade]
            height = sum([surf.get_height() for surf in descriptions]) + 5*(len(name_lines)-1)
            x = 200
            y = surf.get_height()//2 - height//2
            for line in descriptions:
                x = x
                surf.blit(line, (x, y))
                y += line.get_height()

            x = 30
            y = surf.get_height()//2
            pygame.draw.circle(surf, (255, 255, 255), (x, y), 12)
            level = self.frame.game.upgrade_levels[upgrade]
            level_surf = self.level_font.render(str(level), 1, (0, 0, 0))
            surf.blit(level_surf, (x - level_surf.get_width()//2, y - level_surf.get_height()//2 -1))

            surfs.append((upgrade, surf))
        return surfs

