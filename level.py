import pygame as pg
from constants import *
from sprites import Wall, Bullet

class Level:
    def __init__(self):
        self.player_image = pg.transform.scale(IMAGES['player'], (20,20))
        self.player_flip = pg.transform.flip(self.player_image, True, False)
        self.player_rect = self.player_image.get_rect(center=PLAYERPOS)
        self.movex = 0; self.movey = 0
        self.all_sprites = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        walls = [[0, 0, 20, 20], [50, 50, 20, 20], [100, 100, 20, 20]]
        for wall in walls:
            Wall([self.all_sprites, self.walls], *wall)
        self.flip = False

    def update(self, main):
        main.surface.fill(WHITE)
        self.movex, self.movey = check_move('all')
        if self.movex == 1:
            self.flip = True
        elif self.movex == -1:
            self.flip = False
        self.movex = (-self.movex) * 1
        self.movey = (-self.movey) * 1
        self.walls.update(self)
        self.bullets.update(self)
        self.all_sprites.draw(main.surface)
        if self.flip:
            main.surface.blit(self.player_flip, self.player_rect)
        else: main.surface.blit(self.player_image, self.player_rect)
        mouse_pos = list(pg.mouse.get_pos())
        mouse_pos[0] /= 4; mouse_pos[1] /= 4
        angle = math.degrees(math.atan2(mouse_pos[1] - self.player_rect.centery, 
                                        mouse_pos[0] - self.player_rect.centerx))
        left = angle < -90 or angle > 90
        if left: gun = pg.transform.flip(IMAGES['AK-47'], False, True)
        else: gun = IMAGES['AK-47']
        gun = pg.transform.rotate(gun, -angle)
        playerx, playery = self.player_rect.center
        width = gun.get_width(); height = gun.get_height()
        x = playerx - width // 2; y = playery - height // 2
        direction = pg.Vector2(mouse_pos[0] - playerx, mouse_pos[1] - playery)
        direction = direction.normalize()
        x += direction.x * 20; y += direction.y * 20
        main.surface.blit(gun, (x, y))
        if pg.mouse.get_pressed()[0]:
            print(direction)
            Bullet([self.all_sprites, self.bullets], *self.player_rect.center, direction)