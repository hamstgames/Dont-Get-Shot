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
    def __init__(self, groups, x, y, radius, time, withlevel=True):
        super().__init__(groups) # print(radius)
        self.image = pg.Surface((radius*2, radius*2)).convert_alpha()
        self.image.fill((0,0,0,0))
        pg.draw.circle(self.image, YELLOW, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.start = pg.time.get_ticks()
        self.time = time
        self.withlevel = withlevel

    def update(self, level, *_):
        if self.withlevel:
            self.rect.x += level.movex
            self.rect.y += level.movey
        if pg.time.get_ticks() - self.start > self.time: self.kill()
        # make circle bigger
        w = self.rect.width+1; h = self.rect.height+1
        self.image = pg.Surface((w, h)).convert_alpha()
        self.image.fill((0,0,0,0))
        pg.draw.circle(self.image, YELLOW, (w // 2, h // 2), w // 2)
        self.rect = self.image.get_rect(center=self.rect.center)

class Bullet(pg.sprite.Sprite):
    def __init__(self, groups, x, y, direction, angle, speed, damage, killplayer=True):
        super().__init__(groups)
        self.image = IMAGES["bullet"]
        self.image = pg.transform.rotate(self.image, -angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.timer = PressTimer(1000)
        self.explo = PressTimer(0)
        self.timer.start_timer()
        self.explo.start_timer()
        self.speed = speed
        self.damage = damage
        self.killplayer = killplayer

    def update(self, level, *_):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        self.rect.x += level.movex
        self.rect.y += level.movey
        if self.timer.update(): self.kill()
        if not level.touched(self.rect):
            Explosion(self.groups(), *self.rect.center, 5, 100)
            self.kill()
        if self.rect.colliderect(level.player_rect):
            if self.killplayer: level.player_health -= self.damage
            self.kill()
        collisions = pg.sprite.spritecollide(self, level.enemies, False) # pyright: ignore[reportArgumentType]
        for enemy in collisions:
            enemy.health -= self.damage
            for _ in range(3): 
                Blood([level.blood], *self.rect.center, IMAGES["blood2"], randint(0, 360))
            Explosion(self.groups(), *self.rect.center, 5, 100)
            self.kill()
        if self.explo.update():
            Explosion(self.groups(), *self.rect.center, 3, 50, False)
            self.explo.allways_false()

class PBullet(pg.sprite.Sprite):
    def __init__(self, groups, x, y, direction, angle, speed, damage, killplayer=True):
        super().__init__(groups)
        self.image = IMAGES["bullet"]
        self.image = pg.transform.rotate(self.image, -angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.timer = PressTimer(1000)
        self.explo = PressTimer(0)
        self.timer.start_timer()
        self.explo.start_timer()
        self.speed = speed
        self.damage = damage
        self.killplayer = killplayer
        self.last_damaged = None

    def update(self, level, *_):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        self.rect.x += level.movex
        self.rect.y += level.movey
        if self.timer.update(): self.kill()
        if not level.touched(self.rect):
            Explosion(self.groups(), *self.rect.center, 5, 100)
            self.kill()
        if self.rect.colliderect(level.player_rect):
            if self.killplayer: level.player_health -= self.damage
            self.kill()
        collisions = pg.sprite.spritecollide(self, level.enemies, False) # pyright: ignore[reportArgumentType]
        for enemy in collisions:
            if self.last_damaged != enemy: 
                enemy.health -= self.damage
                self.last_damaged = enemy
            for _ in range(3): 
                Blood([level.blood], *self.rect.center, IMAGES["blood2"], randint(0, 360))
            Explosion(self.groups(), *self.rect.center, 5, 100)
        if self.explo.update():
            Explosion(self.groups(), *self.rect.center, 3, 50, False)
            self.explo.allways_false()

class Blood(pg.sprite.Sprite):
    def __init__(self, groups, x, y, surface, angle):
        super().__init__(groups)
        surface = pg.transform.rotate(surface, angle)
        w = surface.get_width(); h = surface.get_height()
        multiplier = (randint(10,50) / 100)
        w *= multiplier; h *= multiplier
        self.image = pg.transform.scale(surface, (w, h // 2))
        self.rect = self.image.get_rect(center=(x, y))
        self.rect.x += round(math.cos(angle * math.pi / 180) * randint(10, 30))
        self.rect.y += round(math.sin(angle * math.pi / 180) * randint(10, 30))
    
    def update(self, level, *_):
        self.rect.x += level.movex
        self.rect.y += level.movey

class Corpse(pg.sprite.Sprite):
    def __init__(self, groups, x, y, surface, level):
        super().__init__(groups)
        w = surface.get_width(); h = surface.get_height()
        self.image = pg.transform.scale(surface, (w, h // 4 * 3))
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = PressTimer(100000)
        self.timer.start_timer()
        for _ in range(5):
            Blood(level.blood, *self.rect.center, IMAGES["blood2"], randint(0, 360))

    def update(self, level, *_):
        self.rect.x += level.movex
        self.rect.y += level.movey
        if self.timer.update(): self.kill()


class Enemy(pg.sprite.Sprite):
    """A Enemy class to subclass"""
    def __init__(self, groups, x, y, image, speed=0):
        super().__init__(groups)
        self.image = image
        self.left = self.image
        self.right = pg.transform.flip(self.image, True, False)
        self.rect: pg.Rect = self.image.get_rect(center=(x, y))
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
            touch_player = False
            for i in range(200):
                x += linex; y += liney
                col_rect = pg.Rect(x, y, 1, 1)
                if col_rect.colliderect(level.player_rect):
                    touch_player = True; break
                if not level.touched(col_rect):
                    touch_player = False; break
                if level.debug:
                    pg.draw.rect(main.surface, RED, col_rect)
            if touch_player:
                self.state = 'chase'
        if self.state == 'chase':
            # do line check if seen player
            player_center = level.player_rect.center
            vector = pg.Vector2(player_center) - pg.Vector2(self.rect.center)
            linex, liney = vector.normalize()
            x = self.rect.centerx; y = self.rect.centery
            touch_player = False
            for i in range(200):
                x += linex; y += liney
                col_rect = pg.Rect(x, y, 1, 1)
                if col_rect.colliderect(level.player_rect):
                    touch_player = True; break
                if not level.touched(col_rect):
                    touch_player = False; break
                if level.debug:
                    pg.draw.rect(main.surface, RED, col_rect)
            if not touch_player:
                self.state = 'idle'
            if vector.magnitude() < 50:
                self.move = 0
            else: self.move = 1
            # set direction to face player
            long = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
            self.direction = math.degrees(math.acos(vector[0] / long))
            if vector[1] < 0: self.direction = 360 - self.direction
            if self.shoot_timer.update():
                pos = [math.cos(math.radians(self.direction)), math.sin(math.radians(self.direction))]
                # make pos move twards to player so the enemy doesn't shoot himself
                move = pg.Vector2(level.player_rect.center)-pg.Vector2(self.rect.center)
                move = move.normalize()
                x = self.rect.centerx + move.x * 20
                y = self.rect.centery + move.y * 20
                Bullet([level.all_sprites, level.bullets], x, y, pos, self.direction, 10, 2)
                self.shoot_timer.start_timer()
        self.rect.x += round(self.speed * math.cos(self.direction) * self.move)
        if not level.touched(self.rect):
            self.rect.x -= round(self.speed * math.cos(self.direction) * self.move)
        self.rect.y += round(self.speed * math.sin(self.direction) * self.move)
        if not level.touched(self.rect):
            self.rect.y -= round(self.speed * math.sin(self.direction) * self.move)
        if self.health <= 0:
            groups = [level.corspes]
            Corpse(groups, *self.rect.center, IMAGES['enemy_dead'], level)
            self.kill()
        if level.debug:
            rect = self.rect.inflate(2, 2)
            pg.draw.rect(main.surface, RED, rect, 1)
        if math.cos(self.direction) > 0:
            self.image = self.right
        else: self.image = self.left