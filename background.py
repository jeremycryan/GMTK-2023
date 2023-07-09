from image_manager import ImageManager
import constants as c


class Background:

    def __init__(self):
        self.surf = ImageManager.load("assets/images/NEW BG 2.png", 1)

    def update(self, dt, events):
        pass

    def draw(self, surf, offset=(0, 0)):
        xoff = offset[0]*0.5
        yoff = offset[1]*0.5
        x = c.WINDOW_WIDTH//2 - self.surf.get_width()//2 + xoff
        y = c.WINDOW_HEIGHT//2 - self.surf.get_height()//2 + yoff
        surf.blit(self.surf, (x, y))
