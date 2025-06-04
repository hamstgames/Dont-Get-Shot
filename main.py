import pygame as pg
from level import Level
from constants import *
pg.init()
pg.mixer.init()

class Main:
    def __init__(self):
        self.running = True
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode(WINSIZE)
        self.surface = pg.Surface(WINSURFACE)
        self.level = Level()
    
    def run_game(self):
        while self.running:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                # put back event for level.py to listen to
                pg.event.post(event)
            self.level.update(self)
            surface = pg.transform.scale(self.surface, WINSIZE)
            self.screen.blit(surface, (0, 0))
            pg.display.flip()
        pg.quit()

if __name__ == '__main__':
    Main().run_game()