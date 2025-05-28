import pygame as pg
from constants import *
from sprites import *

class Level:
    def __init__(self):
        self.player_image = IMAGES['player']
        self.player_flip = pg.transform.flip(self.player_image, True, False)
        self.player_rect:pg.Rect = self.player_image.get_rect(center=PLAYERPOS)
        self.movex = 0; self.movey = 0
        self.all_sprites = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.particles = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.touchable = pg.sprite.Group()
        walls = [[0, 0, 50, 50], [50, 50, 50, 50], [100, 100, 50, 50]]
        for wall in walls:
            Wall([self.all_sprites, self.walls, self.touchable], *wall)
        self.flip = False
        self.shoot_timer = PressTimer(100)

    def touched(self, rect=None):
        rect = self.player_rect if rect is None else rect
        collist = list(self.touchable)
        collisions = rect.collidelist(collist)
        return collisions == -1

    def update(self, main):
        main.surface.fill(WHITE)
        keys = pg.key.get_pressed()
        self.movex, self.movey = 0, 0
        if keys[pg.K_a]:
            self.player_rect.x -= 1
            if self.touched(): self.movex = 1; self.flip = False
            self.player_rect.x += 1
        if keys[pg.K_d]:
            self.player_rect.x += 1
            if self.touched(): self.movex = -1; self.flip = True
            self.player_rect.x -= 1
        if keys[pg.K_w]:
            self.player_rect.y -= 1
            if self.touched(): self.movey = 1
            self.player_rect.y += 1
        if keys[pg.K_s]:
            self.player_rect.y += 1
            if self.touched(): self.movey = -1
            self.player_rect.y -= 1
        self.walls.update(self)
        self.bullets.update(self)
        self.particles.update(self)
        self.all_sprites.draw(main.surface)
        if self.flip:
            main.surface.blit(self.player_flip, self.player_rect)
        else: main.surface.blit(self.player_image, self.player_rect)
        mouse_pos = [float(a) for a in pg.mouse.get_pos()]
        mouse_pos[0] /= WINTIMES; mouse_pos[1] /= WINTIMES
        angle = math.degrees(math.atan2(mouse_pos[1] - self.player_rect.centery, 
                                        mouse_pos[0] - self.player_rect.centerx))
        left = angle < -90 or angle > 90
        if left: gun = pg.transform.flip(IMAGES['AK-47'], False, True)
        else: gun = IMAGES['AK-47']
        gun = pg.transform.rotate(gun, -angle)
        playerx, playery = self.player_rect.center
        rect = gun.get_rect(center=(playerx, playery))
        direction = pg.Vector2(mouse_pos[0] - playerx, mouse_pos[1] - playery)
        direction = direction.normalize()
        rect.x += round(direction.x * 20); rect.y += round(direction.y * 20)
        main.surface.blit(gun, rect)
        if pg.mouse.get_pressed()[0] and self.shoot_timer.update():
            Bullet([self.all_sprites, self.bullets], *rect.center, direction, angle)
            self.shoot_timer.start_timer()