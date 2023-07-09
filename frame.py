import math
import random

import pygame

from background import Background
from constants import *
from grid import Grid, Tile
from hero import Hero
from image_manager import ImageManager
from toss_ui import TossUI
from upgrade_ui import UpgradeUI
from zombie import *


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
        self.since_freeze = 0
        self.since_shake = 1000
        self.shake_amp = 0
        self.stage_clear_font = pygame.font.Font("assets/fonts/edge_of_the_galaxy.otf", 70)
        self.stage_clear_text = self.stage_clear_font.render("Stage Cleared!", True, (255, 255, 255))
        self.stage_clear_caption_font = pygame.font.Font("assets/fonts/segoeui.ttf", 26)
        self.stage_clear_caption_text = self.stage_clear_caption_font.render("The hero has overcome your attacks, for now...", True, (255, 255, 255))
        self.victory_text = self.stage_clear_font.render("Victory!", True, (255, 255, 255))
        self.particles = []
        self.shade = pygame.Surface(WINDOW_SIZE)
        self.shade.fill((0, 0, 0))
        self.midbar = pygame.Surface((WINDOW_WIDTH, 200))
        self.midbar.fill((0, 0, 0))
        self.midbar.set_alpha(160)

    def load_zombies(self):
        self.spawner_count = 0
        if self.level == 1:
            self.spawn_queue.append(Zombie(self, *self.get_spawner()))
            self.spawn_queue.append(FastZombie(self, *self.get_spawner()))
            self.spawn_queue.append(ToughZombie(self, *self.get_spawner()))
            self.spawn_queue.append(BigZombie(self, *self.get_spawner()))
            # for i in range(4):
            #     self.spawn_queue.append(Zombie(self, *self.get_spawner()))
        elif self.level == 2:
            for i in range(2):
                self.spawn_queue.append(Zombie(self, *self.get_spawner()))
            for i in range(2):
                self.spawn_queue.append(BigZombie(self, *self.get_spawner()))
        elif self.level == 3:
            for i in range(5):
                self.spawn_queue.append(Zombie(self, *self.get_spawner()))

    def get_spawner(self):
        self.spawner_count += 1
        return self.grid.tile_to_world(self.zombie_spawners[(self.spawner_count-1) % len(self.zombie_spawners)])

    def update(self, dt, events):
        self.since_freeze += dt
        self.update_shake(dt, events)
        self.upgrade_ui.update(dt, events)
        self.toss_ui.update(dt, events)
        for particle in self.particles[:]:
            particle.update(dt, events)
            if particle.destroyed:
                self.particles.remove(particle)
        dt = self.toss_ui.adjust_time(dt)

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
                if event.key == pygame.K_s:
                    self.shake(15)

        if self.level_end or self.victory:
            self.level_end_timer += dt
            if not self.victory and self.level_end_timer > 2:
                self.done = True
            dt *= 0.1

        if self.since_freeze < 0:
            dt *= 0.001
        self.t += dt

        if self.t > self.spawn_count * SPAWN_RATE:
            if self.spawn_count < len(self.spawn_queue):
                self.zombies.append(self.spawn_queue[self.spawn_count])
                self.spawn_count += 1
            elif not len(self.zombies) and len(self.heros) and not self.level_end and not self.victory:
                self.shake(20)
                self.level += 1
                if True:#self.level <= MAX_LEVEL:
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
            if zombie.hp <= 0:
                self.toss_ui.release_zombie(launch=False)
        self.zombies += grabbed
        for zombie in self.zombies:
            zombie.update(dt, events)
        for projectile in self.projectiles[:]:
            projectile.update(dt, events)
        self.background.update(dt, events)
        if not len(self.heros) and not self.complete:
            self.upgrade_ui.raise_up()
            self.complete = True


    def shake(self, amt=15):
        if amt < self.shake_amp:
            return
        self.since_shake = 0
        self.shake_amp = amt

    def update_shake(self, dt, events):
        self.since_shake += dt
        self.shake_amp *= 0.003**dt
        self.shake_amp -= 10*dt
        if self.shake_amp < 0:
            self.shake_amp = 0

    def freeze(self, duration):
        self.since_freeze = -duration

    def get_shake_offset(self, offset=(0, 0)):
        x = offset[0]
        y = offset[1]
        x += math.cos(self.since_shake*35)*self.shake_amp
        y += math.cos(self.since_shake*32)*self.shake_amp
        return x, y

    def draw(self, surface, offset=(0, 0)):
        # surface.fill((100, 0, 0))
        offset = self.get_shake_offset(offset)
        self.background.draw(surface, offset)
        # self.grid.draw(surface, offset, only=[Tile.AIR])
        if self.level == 1:
            surface.blit(ImageManager.load("assets/images/tutorial.png"), (offset[0], offset[1]))
        for hero in self.heros:
            hero.draw(surface, offset)
        for zombie in self.zombies:
            zombie.draw(surface, offset)
        for projectile in self.projectiles:
            projectile.draw(surface, offset)

        self.grid.draw(surface, offset, only=[Tile.GROUND])
        for particle in self.particles:
            particle.draw(surface, offset)
        self.toss_ui.draw(surface, offset)
        self.upgrade_ui.draw(surface, offset)
        if self.victory or self.level_end:
            surface.blit(self.midbar, (WINDOW_WIDTH//2 - self.midbar.get_width()//2, WINDOW_HEIGHT//2 - self.midbar.get_height()//2 + 40))
        if self.victory:
            surface.blit(self.victory_text, (WINDOW_WIDTH / 2 - self.victory_text.get_width() / 2, WINDOW_HEIGHT / 2))
        if self.level_end:
            surface.blit(self.stage_clear_text, (WINDOW_WIDTH/2 - self.stage_clear_text.get_width()/2, WINDOW_HEIGHT/2))
            surface.blit(self.stage_clear_caption_text, (WINDOW_WIDTH//2 - self.stage_clear_caption_text.get_width()//2, WINDOW_HEIGHT//2 + 65))

        if self.level_end_timer > 1.5:
            self.shade.set_alpha(int(255*2*(self.level_end_timer - 1.5)))
            surface.blit(self.shade, (0, 0))

    def next_frame(self):
        if self.level <= MAX_LEVEL:
            return Frame(self.game, self.level)
        else:
            return GameOverFrame(self.game)


class GameOverFrame(Frame):
    def __init__(self, game):
        super().__init__(game)
        self.back = ImageManager.load("assets/images/victory.png")
        self.font = pygame.font.Font("assets/fonts/segoeui.ttf", 26)
        kills = 0
        for key in self.game.upgrade_levels:
            kills += self.game.upgrade_levels[key]
        self.text = self.font.render(f"You killed the hero {kills} times.", 1, (0, 160, 255))
        self.second_text = self.font.render(f"But you could probably do better.", 1, (255, 255, 255))

    def update(self, dt, events):
        pass

    def draw(self, surf, offset=(0, 0)):
        surf.fill((255, 255, 0))
        surf.blit(self.back, (0, 0))
        surf.blit(self.text, (WINDOW_WIDTH//2 - self.text.get_width()//2, 450))
        surf.blit(self.second_text, (WINDOW_WIDTH//2 - self.second_text.get_width()//2, 450 + self.text.get_height()))