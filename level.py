import pygame as pg

class Level:
    def __init__(self, main):
        self.main = main
        self.display_surface = self.game.display_surface
        self.setup_level_data()
        self.create_level()