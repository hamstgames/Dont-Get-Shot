import pygame as pg
from constants import *
from typing import Any, Iterable, Union

class Wall(pg.sprite.Sprite):
    """A static wall object that blocks movement."""
    def __init__(self, groups, x: int, y: int, width: int, height: int) -> None:
        """Create a wall at (x, y) with given width and height."""
        super().__init__(groups)
        self.image = pg.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        pg.draw.rect(self.image, (100,100,100), self.rect, 0, 5)
        pg.draw.rect(self.image, BLACK, self.rect, 2, 5)
        self.rect.topleft = (x, y)
    
    def update(self, level: Any, *_: Any) -> None:
        """Move wall according to level movement."""
        self.rect.x += level.movex
        self.rect.y += level.movey

class Explosion(pg.sprite.Sprite):
    """An expanding explosion effect that damages enemies."""
    def __init__(self, groups, x: int, y: int, radius: int, time: int, damage: float = 0, withlevel: bool = True, speed: int = 1) -> None:
        """Create an explosion at (x, y) with given radius and duration."""
        super().__init__(groups) # print(radius)
        self.image = pg.Surface((radius*2, radius*2)).convert_alpha()
        self.image.fill((0,0,0,0))
        pg.draw.circle(self.image, YELLOW, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.start = pg.time.get_ticks()
        self.time = time
        self.withlevel = withlevel
        self.damage = damage
        self.speed = speed

    def update(self, level: Any, *_: Any) -> None:
        """Update explosion size and apply damage."""
        if self.withlevel:
            self.rect.x += level.movex
            self.rect.y += level.movey
        if pg.time.get_ticks() - self.start > self.time: self.kill()
        for enemy in pg.sprite.spritecollide(self, level.enemies, False): # pyright: ignore[reportArgumentType]
            enemy.health -= self.damage
            for __ in range(math.ceil(self.damage)): 
                Blood([level.blood], *self.rect.center, get_blood(), randint(0, 360))
        # make circle bigger
        w = self.rect.width + self.speed
        h = self.rect.height + self.speed
        self.image = pg.Surface((w, h)).convert_alpha()
        self.image.fill((0,0,0,0))
        pg.draw.circle(self.image, YELLOW, (w // 2, h // 2), w // 2)
        self.rect = self.image.get_rect(center=self.rect.center)

class Bullet(pg.sprite.Sprite):
    """A bullet projectile that damages enemies or player."""
    def __init__(self, groups, x: int, y: int, direction: pg.Vector2, angle: float, speed: float, damage: float, killplayer: bool = True) -> None:
        """Create a bullet at (x, y) moving in direction."""
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

    def update(self, level: Any) -> None:
        """Move bullet and handle collisions."""
        self.rect.x += round(self.direction[0] * self.speed)
        self.rect.y += round(self.direction[1] * self.speed)
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
                Blood([level.blood], *self.rect.center, get_blood(), randint(0, 360))
            Explosion(self.groups(), *self.rect.center, 5, 100)
            self.kill()
        if self.explo.update():
            Explosion(self.groups(), *self.rect.center, 3, 50, withlevel=False)
            self.explo.allways_false()

class PBullet(pg.sprite.Sprite):
    """A penetrative bullet that can hit multiple enemies."""
    def __init__(self, groups, x: int, y: int, direction: pg.Vector2, angle: float, speed: float, damage: float, killplayer: bool = True) -> None:
        """Create a penetrative bullet at (x, y)."""
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

    def update(self, level: Any) -> None:
        """Move bullet and handle collisions, allowing penetration."""
        self.rect.x += round(self.direction[0] * self.speed)
        self.rect.y += round(self.direction[1] * self.speed)
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
                Blood([level.blood], *self.rect.center, get_blood(), randint(0, 360))
            Explosion(self.groups(), *self.rect.center, 5, 100)
        if self.explo.update():
            Explosion(self.groups(), *self.rect.center, 3, 50, withlevel=False)
            self.explo.allways_false()

class Blood(pg.sprite.Sprite):
    """A blood splatter effect."""
    def __init__(self, groups, x: int, y: int, surface: pg.Surface, angle: float) -> None:
        """Create a blood splatter at (x, y) with given surface and angle."""
        super().__init__(groups)
        surface = pg.transform.rotate(surface, angle)
        w = surface.get_width(); h = surface.get_height()
        multiplier = (randint(10,50) / 100)
        w *= multiplier; h *= multiplier
        self.image = pg.transform.scale(surface, (w, h // 2))
        self.rect = self.image.get_rect(center=(x, y))
        self.rect.x += round(math.cos(angle * math.pi / 180) * randint(10, 30))
        self.rect.y += round(math.sin(angle * math.pi / 180) * randint(10, 30))
    
    def update(self, level: Any, *_: Any) -> None:
        """Move blood splatter according to level movement."""
        self.rect.x += level.movex
        self.rect.y += level.movey

class Corpse(pg.sprite.Sprite):
    """A corpse left behind by dead enemies."""
    def __init__(self, groups, x: int, y: int, surface: pg.Surface, level: Any) -> None:
        """Create a corpse at (x, y) with given surface."""
        super().__init__(groups)
        w = surface.get_width(); h = surface.get_height()
        self.image = pg.transform.scale(surface, (w, h // 4 * 3))
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = PressTimer(1000000)
        self.timer.start_timer()
        for _ in range(5):
            Blood(level.blood, *self.rect.center, get_blood(), randint(0, 360))

    def update(self, level: Any, *_: Any) -> None:
        """Update corpse and spawn blood after a delay."""
        self.rect.x += level.movex
        self.rect.y += level.movey
        if self.timer.update():
            for __ in range(3):
                Blood([level.blood], *self.rect.center, get_blood(), randint(0, 360))
            self.kill()

class Enemy(pg.sprite.Sprite):
    """Enemy character with basic AI and shooting."""
    def __init__(self, groups, x: int, y: int, image: pg.Surface, speed: float = 0) -> None:
        """Create an enemy at (x, y) with given image and speed."""
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

    def update_movement(self, level: Any, main: Any) -> None:
        """Update enemy movement and AI state."""
        if self.state == 'idle':
            self.move = 1
            if random() < 0.1:
                self.direction = randint(0, 360)
            # do line check if seen player
            player_center = level.player_rect.center
            vector = pg.Vector2(player_center) - pg.Vector2(self.rect.center)
            linex, liney = vector.normalize()
            x = self.rect.centerx; y = self.rect.centery
            touch_player = False
            for i in range(200):
                x += linex; y += liney
                col_rect = pg.Rect(x-1, y-1, 2, 2)
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
                col_rect = pg.Rect(x-1, y-1, 2, 2)
                if col_rect.colliderect(level.player_rect):
                    touch_player = True; break
                if not level.touched(col_rect):
                    touch_player = False; break
                if level.debug:
                    pg.draw.rect(main.surface, RED, col_rect)
            if not touch_player:
                self.state = 'idle'
            if vector.magnitude() < 100:
                self.move = 0
            else: self.move = 1
            # set direction to face player
            long = (vector[0] ** 2 + vector[1] ** 2) ** 0.5
            self.direction = math.degrees(math.acos(vector[0] / long))
            if vector[1] < 0: self.direction = 360 - self.direction
            if self.shoot_timer.update():
                pos = pg.Vector2(math.cos(math.radians(self.direction)), 
                                 math.sin(math.radians(self.direction)))
                # make pos move twards to player so the enemy doesn't shoot himself
                move = pg.Vector2(level.player_rect.center)-pg.Vector2(self.rect.center)
                move = move.normalize()
                x = round(self.rect.centerx + move.x * 20)
                y = round(self.rect.centery + move.y * 20)
                Bullet([level.all_sprites, level.bullets], x, y, pos, self.direction, 10, 2)
                self.shoot_timer.start_timer()
        if self.health <= 0:
            groups = [level.corspes]
            Corpse(groups, *self.rect.center, IMAGES['enemy_dead'], level)
            self.kill()
        if math.cos(self.direction) > 0:
            self.image = self.right
        else: self.image = self.left
    
    def update(self, level: Any, main: Any) -> None:
        """Move enemy and handle collisions."""
        self.rect.x += level.movex
        self.rect.y += level.movey
        self.rect.x += round(self.speed * math.cos(self.direction) * self.move)
        if not level.touched(self.rect):
            self.rect.x -= round(self.speed * math.cos(self.direction) * self.move)
        self.rect.y += round(self.speed * math.sin(self.direction) * self.move)
        if not level.touched(self.rect):
            self.rect.y -= round(self.speed * math.sin(self.direction) * self.move)
        if level.debug:
            rect = self.rect.inflate(2, 2)
            pg.draw.rect(main.surface, RED, rect, 1)

class Grenade(pg.sprite.Sprite):
    """A grenade projectile that explodes after a delay or on impact."""
    def __init__(self, groups, x: int, y: int, direction: float, speed: float, damage: float = 1) -> None:
        """Create a grenade at (x, y) moving in direction."""
        super().__init__(*groups)
        images = [IMAGES['burning1'], IMAGES['burning2'], IMAGES['burning3']]
        images = [pg.transform.rotate(image, -direction) for image in images]
        self.images = cycle(images)
        self.image = next(self.images)
        self.rect: pg.Rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.movex = math.cos(math.radians(direction)) * self.speed
        self.movey = math.sin(math.radians(direction)) * self.speed
        self.timer = PressTimer(10000)
        self.timer.start_timer()
        self.damage = damage
        self.change_timer = PulseTimer(300)

    def update(self, level: Any) -> None:
        """Move grenade and check for explosion triggers."""
        self.rect.x += level.movex
        self.rect.y += level.movey
        self.rect.x += round(self.movex)
        self.rect.y += round(self.movey)
        center = self.rect.center
        if self.change_timer.update():
            self.image = next(self.images)
        self.rect = self.image.get_rect(center=center)
        if not level.touched(self.rect):
            self.explode()
        list_ = [x.rect for x in level.enemies]
        if self.rect.collidelist(list_) != -1:
            self.explode()
        if self.timer.update():
            self.explode()

    def explode(self) -> None:
        """Trigger grenade explosion effect."""
        pos = self.rect.center
        Explosion(self.groups(), *pos, 10, 100, self.damage, speed=20)
        self.kill()