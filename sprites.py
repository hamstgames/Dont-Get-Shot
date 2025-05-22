import pygame as pg

class Wall(pg.sprite.Sprite):
    def __init__(self, groups, x, y, width, height):
        super().__init__(groups)
        self.image = pg.Surface((width, height))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
    
    def update(self, level):
        self.rect.x += level.movex
        self.rect.y += level.movey