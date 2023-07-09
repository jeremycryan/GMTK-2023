import random

import pygame

from background import Background
from constants import *
from grid import Grid, Tile
from hero import Hero
from image_manager import ImageManager
from toss_ui import TossUI
from upgrade_ui import UpgradeUI
from zombie import Zombie


class FrameBase:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        pass

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))

    def next_frame(self):
        return Frame(self.game)


class Frame(FrameBase):
    def __init__(self, game, level=1):
        super().__init__(game)
        self.level = level

    def load(self):
        self.grid = Grid(self.level)
        self.zombie_spawners = self.grid.spawners
        self.zombies = []
        self.heros = [Hero(self, *self.grid.tile_to_world(self.grid.heros[0]))]
        self.projectiles = []
        self.toss_ui = TossUI(self)
        self.upgrade_ui = UpgradeUI(self)
        self.background = Background()
        self.t = 0
        self.spawn_count = 0
        self.spawn_queue = []
        self.load_zombies()
        self.complete = False
        self.victory = False
        self.level_end = False
        self.level_end_timer = 0
        self.stage_clear_font = pygame.font.Font("assets/fonts/edge_of_the_galaxy.otf", 70)
        self.stage_clear_text = self.stage_clear_font.render("Stage Cleared!", True, (255, 255, 255))
        self.victory_text = self.stage_clear_font.render("Victory!", True, (255, 255, 255))

    def load_zombies(self):
        if self.level == 1:
            for i in range(4):
                spawner = self.grid.tile_to_world(self.zombie_spawners[i % len(self.zombie_spawners)])
                self.spawn_queue.append(Zombie(self, *spawner))
        elif self.level == 2:
            for i in range(6):
                spawner = self.grid.tile_to_world(self.zombie_spawners[i % len(self.zombie_spawners)])
                self.spawn_queue.append(Zombie(self, *spawner))

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.zombies = []
                    self.spawn_queue = []
                if self.level_end or self.victory and event.key == pygame.K_RETURN:
                    self.done = True
                    if self.victory:
                        self.level = 1
                        self.game.upgrade_levels = {key: 0 for key in UPGRADE_NAMES}

        if self.level_end or self.victory:
            self.level_end_timer += dt
            if not self.victory and self.level_end_timer > 1:
                self.done = True
            return
        self.upgrade_ui.update(dt, events)
        self.toss_ui.update(dt, events)
        dt = self.toss_ui.adjust_time(dt)
        self.t += dt

        if self.t > self.spawn_count * SPAWN_RATE:
            if self.spawn_count < len(self.spawn_queue):
                self.zombies.append(self.spawn_queue[self.spawn_count])
                self.spawn_count += 1
            elif not len(self.zombies):
                self.level += 1
                if self.level <= MAX_LEVEL:
                    self.level_end = True
                else:
                    self.victory = True

        self.grid.update(dt, events)
        for hero in self.heros:
            hero.update(dt, events)
        grabbed = []
        for zombie in self.zombies[:]:
            if zombie.grabbed:
                self.zombies.remove(zombie)
                grabbed.append(zombie)
            zombie.update(dt, events)
        self.zombies += grabbed
        for projectile in self.projectiles[:]:
            projectile.update(dt, events)
        self.background.update(dt, events)
        if not len(self.heros) and not self.complete:
            self.upgrade_ui.raise_up()
            self.complete = True

    def draw(self, surface, offset=(0, 0)):
        # surface.fill((100, 0, 0))
        self.background.draw(surface, offset)
        # self.grid.draw(surface, offset, only=[Tile.AIR])
        if self.level == 1:
            surface.blit(ImageManager.load("assets/images/tutorial.png"), (0, 0))
        for hero in self.heros:
            hero.draw(surface, offset)
        for zombie in self.zombies:
            zombie.draw(surface, offset)
        for projectile in self.projectiles:
            projectile.draw(surface, offset)
        self.grid.draw(surface, offset, only=[Tile.GROUND])
        self.toss_ui.draw(surface, offset)
        self.upgrade_ui.draw(surface, offset)
        if self.victory:
            surface.blit(self.victory_text, (WINDOW_WIDTH / 2 - self.victory_text.get_width() / 2, WINDOW_HEIGHT / 2))
        if self.level_end:
            surface.blit(self.stage_clear_text, (WINDOW_WIDTH/2 - self.stage_clear_text.get_width()/2, WINDOW_HEIGHT/2))

    def next_frame(self):
        return Frame(self.game, self.level)
