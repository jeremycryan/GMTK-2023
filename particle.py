import pygame

from image_manager import ImageManager
from pyracy.sprite_tools import Sprite, Animation


class Particle:

    def __init__(self, duration, position, velocity):
        self.age = 0
        self.duration = duration
        self.x = position[0]
        self.y = position[1]
        self.vx = velocity[0]
        self.vy = velocity[1]
        self.destroyed = False

    def through(self, exp=1):
        return min(self.age/self.duration, 1)**exp

    def destroy(self):
        self.destroyed = True

    def draw(self, surf, offset=(0, 0)):
        if self.destroyed:
            return

    def update(self, dt, events):
        self.age += dt
        if self.age > self.duration:
            self.destroy()
        self.x += self.vx*dt
        self.y += self.vy*dt


class Spatter(Particle):
    def __init__(self, position, angle):
        super().__init__(0.5, position, (0, 0))
        self.angle = angle  # degrees
        self.sprite = Sprite(30, position)
        self.sprite.add_animation({
            "base": Animation(ImageManager.load("assets/images/blood spatter 30fps.png", 0.7), (5, 1), 5),
        })
        self.sprite.start_animation("base")
        self.sprite.add_callback("base", self.destroy)

    def update(self, dt, events):
        super().update(dt, events)
        self.sprite.update(dt, events)

    def draw(self, surf, offset=(0, 0)):
        img = self.sprite.get_image()
        img = pygame.transform.rotate(img, self.angle)
        x = self.x - img.get_width()//2
        y = self.y - img.get_height()//2
        surf.blit(img, (x + offset[0], y + offset[1]))

class Land(Particle):
    def __init__(self, position):
        super().__init__(0.5, position, (0, 0))
        self.sprite = Sprite(30, position)
        self.scale = 1
        self.sprite.add_animation({
            "base": Animation(ImageManager.load("assets/images/landing particle effect.png", 0.5), (4, 1), 4),
        })
        self.sprite.start_animation("base")
        self.sprite.add_callback("base", self.destroy)

    def update(self, dt, events):
        super().update(dt, events)
        self.sprite.update(dt, events)

    def draw(self, surf, offset=(0, 0)):
        img = self.sprite.get_image()
        img = pygame.transform.scale(img, (img.get_width()*self.scale, img.get_height()*self.scale))
        x = self.x - img.get_width()//2
        y = self.y - img.get_height()//2
        surf.blit(img, (x + offset[0], y + offset[1]))

class Death(Particle):
    def __init__(self, position):
        super().__init__(1000, position, (0, 0))
        self.x = position[0]
        self.y = position[1]
        self.sprite = Sprite(6, position)
        self.sprite.add_animation({
            "base": Animation(ImageManager.load("assets/images/man dying 24fps.png", 0.5), (2, 1), 2),
            "dead": Animation(ImageManager.load("assets/images/man death 0fps.png", 0.5), (1, 1), 1)
        }, loop=True)
        self.sprite.start_animation("base")

    def update(self, dt, events):
        super().update(dt, events)
        self.sprite.update(dt, events)
        if self.age > 2:
            self.sprite.start_animation("dead")

    def draw(self, surf, offset=(0, 0)):
        self.sprite.x = self.x + offset[0]
        self.sprite.y = self.y + offset[1]
        self.sprite.draw(surf, offset)