import pygame as pg
pg.init()
from level import Level

class Main:
    def __init__(self):
        self.level = Level()
        self.run = True
        self.clock = pg.time.Clock()
        self.dt = 0
        self.fps = 60
        self.screen = pg.display.set_mode((1280, 720))