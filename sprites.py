import pygame as pg
from constants import *

class Wall(pg.sprite.Sprite):
    def __init__(self, groups, x, y, width, height):
        super().__init__(groups)
        self.image = pg.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        pg.draw.rect(self.image, (100,100,100), self.rect, 0, 5)
        pg.draw.rect(self.image, BLACK, self.rect, 2, 5)
        self.rect.topleft = (x, y)
    
    def update(self, level):
        self.rect.x += level.movex
        self.rect.y += level.movey

class Bullet(pg.sprite.Sprite):
    def __init__(self, groups, x, y, direction, angle, speed):
        super().__init__(groups)
        self.image = IMAGES["bullet"]
        self.image = pg.transform.rotate(self.image, -angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.timer = PressTimer(1000)
        self.timer.start_timer()
        self.speed = speed

    def update(self, level):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        self.rect.x += level.movex
        self.rect.y += level.movey
        if self.timer.update(): self.kill()
        if not level.touched(self.rect): self.kill()