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

        self.shade = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill((0, 0, 0))
        self.shade.set_colorkey((255, 255, 255))
        self.shade.set_alpha(0)

        self.title_font = pygame.font.Font("assets/fonts/edge_of_the_galaxy.otf", 70)
        self.title_surf = self.title_font.render("Hero level up!", 1, (255, 255, 255))
        self.subtitle_font = pygame.font.Font("assets/fonts/segoeui.ttf", 22)
        self.subtitle_font_surfs = [
            self.subtitle_font.render("You've beaten him for now,", 1, (255, 255, 255)),
            self.subtitle_font.render("but he'll come back even stronger.", 1, (255, 255, 255)),
        ]

        self.upgrade_surfs = []
        self.upgrade_name_font = pygame.font.Font("assets/fonts/edge_of_the_galaxy.otf", 27)
        self.upgrade_names = {name:[self.upgrade_name_font.render(line.upper(), 1, (255, 255, 255)) for line in c.UPGRADE_NAMES[name].split()] for name in c.UPGRADE_NAMES}
        self.upgrade_description_font = self.subtitle_font
        self.upgrade_descriptions = {name:self.upgrade_description_font.render(c.UPGRADE_DESCRIPTIONS[name], 1, (255, 255, 255)) for name in c.UPGRADE_NAMES}

    def raise_up(self):
        self.active = True
        self.upgrade_surfs = self.get_upgrade_surfs()

    def update(self, dt, events):
        if self.active:
            self.activeness += dt/UpgradeUI.FADE_IN_TIME
            if self.activeness > 1:
                self.activeness = 1
        else:
            self.activeness -= dt/UpgradeUI.FADE_IN_TIME
            if self.activeness < 0:
                self.activeness = 0

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.process_click()
                if self.active:
                    events.remove(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_o:
                    self.raise_up()

    def process_click(self):
        mpos = pygame.mouse.get_pos()
        x = c.WINDOW_WIDTH//2
        y = c.WINDOW_HEIGHT//2 + 10
        for key, up_surf in self.upgrade_surfs:
            rect = pygame.Rect(x, y, up_surf.get_width(), up_surf.get_height)
            if rect.collidepoint(*mpos):
                self.select_upgrade(key)

    def select_upgrade(self, key):
        self.frame.game.upgrade_levels[key] += 1
        self.active = False

    def draw(self, surf, offset=(0, 0)):
        if self.activeness <= 0:
            return

        self.shade.set_alpha(180*self.activeness)
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
            surf.blit(up_surf, (x - up_surf.get_width()//2, y - up_surf.get_height()//2))
            y += up_surf.get_height() + 15

    def get_upgrade_surfs(self):
        surfs = []
        possible_upgrades = list(c.UPGRADE_NAMES)
        for i in range(3):
            if not possible_upgrades:
                continue
            upgrade = random.choice(possible_upgrades)
            possible_upgrades.remove(upgrade)
            surf = ImageManager.load_copy("assets/images/upgrade_outline.png")

            name_lines = self.upgrade_names[upgrade]

            height = sum([surf.get_height() for surf in name_lines]) + 5*(len(name_lines)-1)
            y = surf.get_height()//2 - height//2 + 2
            for line in name_lines:
                x = 160 - line.get_width()
                surf.blit(line, (x, y))
                y += line.get_height()+5

            description = self.upgrade_descriptions[upgrade]
            x = 200
            y = surf.get_height()//2 - description.get_height()//2
            surf.blit(description, (x, y))


            surfs.append((upgrade, surf))
        return surfs

