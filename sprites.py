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
    
    def update(self, level, *_):
        self.rect.x += level.movex
        self.rect.y += level.movey

class Explosion(pg.sprite.Sprite):
    def __init__(self, groups, x, y, surface, time):
        super().__init__(groups)
        self.image = pg.transform.rotate(surface, randint(0, 360))
        self.rect = self.image.get_rect(center=(x, y))
        self.start = pg.time.get_ticks()
        self.time = time

    def update(self, level, *_):
        self.rect.x += level.movex
        self.rect.y += level.movey
        if pg.time.get_ticks() - self.start > self.time:
            self.kill()

class Bullet(pg.sprite.Sprite):
    def __init__(self, groups, x, y, direction, angle, speed, damage):
        super().__init__(groups)
        self.image = IMAGES["bullet"]
        self.image = pg.transform.rotate(self.image, -angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.timer = PressTimer(1000)
        self.timer.start_timer()
        self.speed = speed
        self.damage = damage

    def update(self, level, *_):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        self.rect.x += level.movex
        self.rect.y += level.movey
        if self.timer.update(): self.kill()
        if not level.touched(self.rect):
            Explosion(self.groups(), *self.rect.center, IMAGES["bullet_explode"], 100)
            self.kill()
        if self.rect.colliderect(level.player_rect):
            level.player_health -= self.damage; self.kill()
        collisions = pg.sprite.spritecollide(self, level.enemies, False) # pyright: ignore[reportArgumentType]
        for enemy in collisions:
            enemy.health -= self.damage
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
        self.shoot_timer = PressTimer(1000)
        self.shoot_timer.start_timer()
        self.move = 1
        self.health = 5

    def update(self, level, main):
        self.rect.x += level.movex
        self.rect.y += level.movey
        if self.state == 'idle':
            self.move = 1
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
                # pg.draw.rect(main.surface, RED, pg.Rect(x, y, 1, 1))
            else:
                if vector.magnitude() < 200:
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
                # pg.draw.rect(main.surface, RED, pg.Rect(x, y, 1, 1))
            if vector.magnitude() > 200:
                self.state = 'idle'
            if vector.magnitude() < 50:
                self.move = 0
            else: self.move = 1
            # set direction to face player
            long = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
            self.direction = math.degrees(math.acos(vector[0] / long))
            if vector[1] < 0: self.direction = 360 - self.direction
            if self.shoot_timer.update():
                pos = (math.cos(math.radians(self.direction)), math.sin(math.radians(self.direction)))
                # make pos move twards to player so the enemy doesn't shoot himself
                move = pg.Vector2(level.player_rect.center)-pg.Vector2(self.rect.center)
                move = move.normalize(); pos = tuple(pg.Vector2(pos) + move * 5)
                Bullet([level.all_sprites, level.bullets], self.rect.centerx, self.rect.centery, pos, self.direction, 5, 2)
                self.shoot_timer.start_timer()
        self.rect.x += self.speed * math.cos(self.direction) * self.move
        if not level.touched(self.rect):
            self.rect.x -= self.speed * math.cos(self.direction) * self.move
        self.rect.y += self.speed * math.sin(self.direction) * self.move
        if not level.touched(self.rect):
            self.rect.y -= self.speed * math.sin(self.direction) * self.move
        if self.health <= 0: self.kill()