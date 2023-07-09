import pygame
import asyncio
import sys

import constants as c
import frame as f
from image_manager import ImageManager
from sound_manager import SoundManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        SoundManager.init()
        ImageManager.init()
        self.upgrade_levels = {key: 0 for key in c.UPGRADE_NAMES}

        pygame.mixer.music.load("assets/audio/game track.ogg")
        pygame.mixer.music.set_volume(0.25)
        pygame.mixer.music.play(-1)

        asyncio.run(self.main())

    def get_upgrade_level(self, key):
        return self.upgrade_levels[key] if key in self.upgrade_levels else 0

    async def main(self):
        current_frame = f.Frame(self)
        current_frame.load()
        self.clock.tick(60)

        while True:
            dt, events = self.get_events()
            await asyncio.sleep(0)
            if dt == 0:
                dt = 1/100000
            pygame.display.set_caption(f"{c.CAPTION} ({int(1/dt)} FPS)")
            if dt > 0.05:
                dt = 0.05
            current_frame.update(dt, events)
            await asyncio.sleep(0)
            current_frame.draw(self.screen, (0, 0))
            pygame.display.flip()

            if current_frame.done:
                current_frame = current_frame.next_frame()
                current_frame.load()

    def get_events(self):
        dt = self.clock.tick()/1000

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        return dt, events


if __name__ == "__main__":
    Game()
