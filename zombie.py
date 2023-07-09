import math
import random

import pygame

from platform_object import PlatformObject
from constants import *

from image_manager import ImageManager
from pyracy.sprite_tools import Sprite, Animation
from sound_manager import SoundManager


class Zombie(PlatformObject):
    IDLE = 0
    WALKING = 1
    BALLISTIC = 2
    GRABBED = 3
    LANDING = 4

    def __init__(self, frame, x, y, w=52, h=52, scale_by=0.5, name="ZR"):
        super().__init__(frame, x, y, w, h, r=w/2)

        self.sprite = Sprite(12)
        self.state = Zombie.IDLE
        self.hp = 2
        self.death_time = 0.2
        self.grabbed = False
        self.cooldown = 0
        self.damage = 1
        self.dead = False
        self.speed = ZOMBIE_SPEED
        self.launch_speed = 1
        self.paused = None

        fling = Animation(ImageManager.load(f"assets/images/{name} Throw 12fps.png", scale_by=scale_by), (4, 1), 4)
        fling_right = Animation(ImageManager.load(f"assets/images/{name} Throw 12fps.png", scale_by=scale_by), (4, 1), 4, reverse_x=True)
        idle = Animation(ImageManager.load(f"assets/images/{name} Walk 6fps.png", scale_by=scale_by), (6, 1), 6, time_scaling = .8)
        idle_right = Animation(ImageManager.load(f"assets/images/{name} Walk 6fps.png", scale_by=scale_by), (6, 1), 6, reverse_x=True, time_scaling = .8)
        hold = Animation(ImageManager.load(f"assets/images/{name} held 12fps.png", scale_by=scale_by), (5, 1), 5)
        hold_right = Animation(ImageManager.load(f"assets/images/{name} held 12fps.png", scale_by=scale_by), (5, 1), 5, reverse_x=True)
        falling = Animation(ImageManager.load(f"assets/images/{name} Fall 6fps.png", scale_by=scale_by), (2, 1), 2)
        falling_right = Animation(ImageManager.load(f"assets/images/{name} Fall 6fps.png", scale_by=scale_by), (2, 1), 2, reverse_x=True)
        land = Animation(ImageManager.load(f"assets/images/{name} Land 0fps.png", scale_by=scale_by), (1, 1), 1)
        land_right = Animation(ImageManager.load(f"assets/images/{name} Land 0fps.png", scale_by=scale_by), (1, 1), 1, reverse_x=True)
        hit = Animation(ImageManager.load(f"assets/images/{name} Hit 6fps.png", scale_by=scale_by), (2, 1), 2)
        hit_right = Animation(ImageManager.load(f"assets/images/{name} Hit 6fps.png", scale_by=scale_by), (2, 1), 2, reverse_x=True)
        bite = Animation(ImageManager.load(f"assets/images/{name} Bite 12fps.png", scale_by=scale_by), (3, 1), 3)
        bite_right = Animation(ImageManager.load(f"assets/images/{name} Bite 12fps.png", scale_by=scale_by), (3, 1), 3, reverse_x=True)
        self.sprite.add_animation(
            {
                "fling_left": fling,
                "fling_right": fling_right,
                "idle_left": idle,
                "idle_right": idle_right,
                "hold_left": hold,
                "hold_right": hold_right,
                "falling_left": falling,
                "falling_right": falling_right,
                "land_left": land,
                "land_right": land_right,
                "hit_left": hit,
                "hit_right": hit_right,
                "bite_left": bite,
                "bite_right": bite_right,
            },
            loop=True,
        )
        self.sprite.chain_animation("land_left", "idle_left")
        self.sprite.chain_animation("land_right", "idle_right")
        self.sprite.add_callback("hit_right", self.on_hit)
        self.sprite.add_callback("hit_left", self.on_hit)
        self.sprite.add_callback("land_left", self.on_land, [True])
        self.sprite.add_callback("land_right", self.on_land, [False])
        self.sprite.start_animation("idle_left")
        SoundManager.load(f"assets/audio/ZR_hurt_1.ogg")
        SoundManager.load(f"assets/audio/ZR_hurt_2.ogg")
        SoundManager.load(f"assets/audio/ZR_hurt_3.ogg")
        SoundManager.load(f"assets/audio/ZR_hurt_4.ogg")
        SoundManager.load(f"assets/audio/ZR_landing_thud_1.ogg")
        SoundManager.load(f"assets/audio/ZR_landing_thud_2.ogg")
        for i in range(7):
            SoundManager.load(f"assets/audio/ZR_launch_{i+1}.ogg")


        self.agape = False

        if self.ballistic:
            self.on_become_ballistic()

        self.squash = 1.0

    def on_hit(self):
        self.sprite.start_animation(self.paused)
        self.paused = None
        self.squash = 1

    def die(self):
        self.grabbed = False
        self.dead = True

    def update(self, dt, events):
        """ Walk around randomly once zombie is grounded """
        super().update(dt, events)
        if not self.dead and self.hp <= 0:
            self.die()
        if self.dead:
            self.grabbed = False
            self.death_time -= dt
            if self.death_time <= 0:
                self.frame.zombies.remove(self)
            return
        self.cooldown -= dt
        if self.cooldown <= 0:
            self.attack()
        if self.grabbed:
            self.state = Zombie.GRABBED
            self.ballistic = False
            self.vx = 0
            self.vy = 0
            #self.x, self.y = pygame.mouse.get_pos()

        if not self.ballistic and not self.grabbed and not self.state == Zombie.LANDING:
            if self.vx_des > 0:
                self.vx_des = self.speed
                if not self.paused:
                    self.sprite.start_animation("idle_right", restart_if_active=False)
            elif self.vx_des < 0:
                self.vx_des = -self.speed
                if not self.paused:
                    self.sprite.start_animation("idle_left", restart_if_active=False)
            else:
                self.vx_des = self.speed if random.random() > 0.5 else -self.speed
        self.sprite.update(dt, events)

        if self.state == Zombie.IDLE:
            ds = 1.0 - self.squash
            if ds:
                self.squash += ds*dt*15
            if abs(self.squash - 1) < 0.05:
                self.squash = 1

    def draw(self, surface, offset):
        super().draw(surface, offset)
        my_surf = self.sprite.get_image()
        direction = "left" if self.vx < 0 else "right"
        if self.death_time <= 0:
            pass  # TODO: death animation
        if self.state == Zombie.BALLISTIC and not self.grabbed:
            if self.vy < 0 and self.agape:
                self.sprite.start_animation(f"fling_{direction}", restart_if_active=False)
                angle = math.atan2(-self.vy, self.vx) + (math.pi if self.vx < 0 else 0)
                my_surf = pygame.transform.rotate(my_surf, math.degrees(angle))
            else:
                self.agape = False
                if not self.paused:
                    self.sprite.start_animation(f"falling_{direction}", restart_if_active=False)
                    self.squash = max(1/(1 + abs(self.vy)*0.0005), 0.7)
        if self.paused:
            self.squash = 1

        if self.grabbed:
            self.sprite.start_animation(f"hold_{direction}", restart_if_active=False)
        if self.squash != 1.0:
            my_surf = pygame.transform.scale(my_surf, (my_surf.get_width()*self.squash, my_surf.get_height()*(1/self.squash)))
        x = self.x + offset[0] - my_surf.get_width()//2
        y = self.y + offset[1] - my_surf.get_height()//2
        surface.blit(my_surf, (x, y))

    def on_become_ballistic(self):
        super().on_become_ballistic()
        if self.grabbed:
            return
        if self.vy < 0:
            self.agape = True
            if self.vx < 0:
                self.sprite.start_animation("fling_left")
            else:
                self.sprite.start_animation("fling_right")
            i = random.randint(1, 7)
            sound = SoundManager.load(f"assets/audio/ZR_launch_{i}.ogg")
            sound.set_volume(0.6)
            sound.play()
        else:
            self.sprite.start_animation("falling_left")
        self.state = Zombie.BALLISTIC
        self.vx_des = math.copysign(self.speed, self.vx)

    def on_become_grounded(self):
        super().on_become_grounded()
        if self.grabbed:
            return
        direction = "left" if ("left" in self.sprite.active_animation_key) else "right"
        self.sprite.start_animation(f"land_{direction}")
        self.state = Zombie.LANDING
        self.frame.shake(3)
        i = random.randint(1, 3)
        SoundManager.load(f"assets/audio/ZR_landing_thud_{i}.ogg").play()

    def on_land(self, left=True):
        if left:
            self.sprite.start_animation(f"idle_left")
        else:
            self.sprite.start_animation(f"idle_right")
        self.squash = 1.3
        self.state = Zombie.IDLE

    def hit(self, damage):
        if not self.paused:
            self.paused = self.sprite.active_animation_key
            if self.vx > 0:
                self.sprite.start_animation("hit_right")
            else:
                self.sprite.start_animation("hit_left")
        self.hp -= damage
        self.frame.shake(15)
        self.frame.freeze(0.125)
        i = random.randint(1, 4)
        SoundManager.load(f"assets/audio/ZR_hurt_{i}.ogg").play()

    def on_collision(self, tile_type, tile_rect):
        dx, dy = self.get_tile_range()
        if tile_rect.top < self.y < tile_rect.bottom:
            if tile_rect.left >= self.x + dx and self.vx_des > 0:
                self.vx_des = -self.vx_des
            if tile_rect.right <= self.x - dx and self.vx_des < 0:
                self.vx_des = -self.vx_des

    def attack(self):
        for hero in self.frame.heros:
            if self.collide(hero.get_rect()):
                self.paused = self.sprite.active_animation_key
                if hero.x > self.x:
                    self.sprite.start_animation("bite_right")
                else:
                    self.sprite.start_animation("bite_left")
                hero.hit(self.damage)
                self.hit(1000)
                hero.vx += math.copysign(ZOMBIE_KNOCKBACK, self.vx_des)
                self.vx += math.copysign(ZOMBIE_KNOCKBACK, self.x - hero.x)
                self.cooldown = ZOMBIE_COOLDOWN
                break


class BigZombie(Zombie):
    def __init__(self, frame, x, y):
        s = 1.6
        super().__init__(frame, x, y, w=int(52 * s), h=int(52 * s), scale_by=s/2)
        self.hp = 1
        self.damage = 3

    def on_become_grounded(self):
        super().on_become_grounded()
        self.frame.shake(7)

    def hit(self, damage):
        super().hit(damage)
        if self.hp <= 0:
            z1 = Zombie(self.frame, self.x+5, self.y)
            z2 = Zombie(self.frame, self.x-5, self.y)
            z3 = Zombie(self.frame, self.x, self.y-5)
            z1.vx += 100
            z2.vx -= 100
            z3.vy -= 100
            z1.vx_des = z1.speed
            z2.vx_des = -z2.speed
            z3.vx_des = self.vx_des
            self.frame.zombies.append(z1)
            self.frame.zombies.append(z2)
            self.frame.zombies.append(z3)


class FastZombie(Zombie):
    def __init__(self, frame, x, y):
        super().__init__(frame, x, y, name="ZRHyper")
        self.speed *= 10


class ToughZombie(Zombie):
    def __init__(self, frame, x, y):
        s = 1
        super().__init__(frame, x, y, w=int(52 * s), h=int(52 * s), scale_by=s/2, name="ZRTough")
        self.hp = 4
