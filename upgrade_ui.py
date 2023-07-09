import pygame
import constants as c


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

    def raise_up(self):
        self.active = True

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
                if self.active:
                    events.remove(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.raise_up()

    def draw(self, surf, offset=(0, 0)):
        if self.activeness <= 0:
            return

        self.shade.set_alpha(180*self.activeness)
        surf.blit(self.shade, (0, 0))

        x = c.WINDOW_WIDTH//2 - self.title_surf.get_width()//2
        y = c.WINDOW_HEIGHT//2 - self.title_surf.get_height()//2 - 155
        surf.blit(self.title_surf, (x, y))

        yoff = 0
        for line in self.subtitle_font_surfs:
            x = c.WINDOW_WIDTH//2 - line.get_width()//2
            y = c.WINDOW_HEIGHT//2 - line.get_height()//2 - 100 + yoff
            surf.blit(line, (x, y))
            yoff += 27

    def get_upgrade_surfs(self):
        pass