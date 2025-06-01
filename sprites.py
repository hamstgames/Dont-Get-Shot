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

class Explosion(pg.sprite.Sprite):
    def __init__(self, groups, x, y, surface, time):
        super().__init__(groups)
        self.image = pg.transform.rotate(surface, randint(0, 360))
        self.rect = self.image.get_rect(center=(x, y))
        self.start = pg.time.get_ticks()
        self.time = time

    def update(self, level):
        self.rect.x += level.movex
        self.rect.y += level.movey
        if pg.time.get_ticks() - self.start > self.time:
            self.kill()

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
        if not level.touched(self.rect):
            Explosion(self.groups(), *self.rect.center, IMAGES["bullet_explode"], 100)
            self.kill()

class Enemy(pg.sprite.Sprite):
    """A Enemy class to subclass"""
    def __init__(self, groups, x, y, image, speed=0):
        super().__init__(groups)
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.state = 'idle'
        self.direction = 0 # direction in degrees

    def update(self, level):
        self.rect.x += level.movex
        self.rect.y += level.movey
        if self.state == 'idle':
            if random() < 0.01:
                self.direction = randint(0, 360)
            # do line check if seen player
            player_center = level.player_rect.center
            vector = pg.Vector2(player_center) - pg.Vector2(self.rect.center)
            linex, liney = vector.normalize()
            x = self.rect.centerx; y = self.rect.centery
            for i in range(100):
                x += linex; y += liney
                if not level.touched(pg.Rect(x, y, 1, 1)):
                    break
            else:
                if vector.magnitude() < 100:
                    self.state = 'chase'
        if self.state == 'chase':
            # do line check if seen player
            player_center = level.player_rect.center
            vector = pg.Vector2(player_center) - pg.Vector2(self.rect.center)
            linex, liney = vector.normalize()
            x = self.rect.centerx; y = self.rect.centery
            for i in range(100):
                x += linex; y += liney
                if not level.touched(pg.Rect(x, y, 1, 1)):
                    self.state = 'idle'
                    break
            if vector.magnitude() > 100:
                self.state = 'idle'
            # set direction to face player
            self.direction = math.degrees(math.atan2(vector.x, vector.y))
            self.direction = self.direction % 360
        print(self.state)
        self.rect.x += self.speed * math.cos(self.direction)
        self.rect.y += self.speed * math.sin(self.direction)