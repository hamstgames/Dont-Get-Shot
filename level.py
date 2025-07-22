import pygame as pg
from constants import *
from sprites import *

class Level:
    """Main game level logic, including player, enemies, inventory, and update loop."""
    def __init__(self):
        """Initialize the level, player, enemies, and inventory."""
        self.player_image = IMAGES['player']
        self.player_flip = pg.transform.flip(self.player_image, True, False)
        self.player_rect:pg.Rect = self.player_image.get_rect(center=PLAYERPOS)
        self.player_health = PLAYERHEALTH
        self.movex = 0; self.movey = 0
        self.all_sprites = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.particles = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.touchable = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.blood = pg.sprite.Group()
        self.corspes = pg.sprite.Group()
        walls = [[0, 0, 50, 50], [50, 50, 50, 50], [100, 100, 50, 50]]
        for wall in walls:
            Wall([self.all_sprites, self.walls, self.touchable], *wall)
        Wall([self.all_sprites, self.walls, self.touchable], -100, -500, 50, 1000)
        Wall([self.all_sprites, self.walls, self.touchable], 500, -500, 50, 1000)
        self.flip = False
        self.shoot_timer = PressTimer(100)
        self.inventory = ['Budget Revolver','High Caliber Pistol','AK - 47','Regular Shotgun','M(16)op Gun','Kriss SuperV','MP - 5',
                          'Grenade Launcher','UZI','B - 25','Big & Heavy','Double Barrel','Trash 5Run','Sniper Rifle','Golden Pistol']
        self.inventory_index = 0; self.gunmode = 0
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        self.tick_timer = PulseTimer(1000 / TPS)
        self.debug = True
        self.player_knockback = pg.Vector2(0, 0)
        self.fps_list = []
        self.inventory_open = False
        self.inventory_selected = 0

    def touched(self, rect=None):
        """Check if the given rect collides with any touchable object."""
        rect = self.player_rect if rect is None else rect
        collist = list(self.touchable)
        collisions = rect.collidelist(collist)
        return collisions == -1

    def update(self, main):
        """Update the game state or show inventory if open."""
        if self.inventory_open:
            self.handle_inventory_ui(main)
        else:
            fps = main.clock.get_fps()
            self.fps_list.append(fps)
            if len(self.fps_list) > 10: self.fps_list.pop(0)
            # try: fps = round(FPS / fps)
            # except: fps = 0
            main.surface.fill(GRAY)
            keys = pg.key.get_pressed()
            self.movex, self.movey = 0, 0
            if keys[pg.K_a]:
                self.player_rect.x -= PLAYERSPEED
                if self.touched(): self.movex = PLAYERSPEED; self.flip = False
                self.player_rect.x += PLAYERSPEED
            if keys[pg.K_d]:
                self.player_rect.x += PLAYERSPEED
                if self.touched(): self.movex = -PLAYERSPEED; self.flip = True
                self.player_rect.x -= PLAYERSPEED
            if keys[pg.K_w]:
                self.player_rect.y -= PLAYERSPEED
                if self.touched(): self.movey = PLAYERSPEED
                self.player_rect.y += PLAYERSPEED
            if keys[pg.K_s]:
                self.player_rect.y += PLAYERSPEED
                if self.touched(): self.movey = -PLAYERSPEED
                self.player_rect.y -= PLAYERSPEED
            vector = pg.Vector2(self.movex, self.movey)
            if vector: vector.normalize_ip()
            self.movex = vector.x * PLAYERSPEED; self.movey = vector.y * PLAYERSPEED
            self.player_rect.x += round(self.player_knockback.x)
            knockx = round(self.player_knockback.x)
            if self.touched(): self.movex  -= self.player_knockback.x
            else: self.player_knockback.x = 0
            self.player_rect.x -= knockx
            self.player_rect.y += round(self.player_knockback.y)
            knocky = round(self.player_knockback.y)
            if self.touched(): self.movey -= self.player_knockback.y
            else: self.player_knockback.y = 0
            self.player_rect.y -= knocky
            if not self.touched():
                self.movex += knockx; self.movey += knocky
                self.player_knockback.x = 0; self.player_knockback.y = 0
            self.player_knockback.x *= 0.8
            self.player_knockback.y *= 0.8
            for event in pg.event.get(pg.KEYDOWN):
                if event.key == pg.K_i:
                    self.inventory_open = not self.inventory_open
                    continue  # Don't process other controls if toggling inventory
                if not self.inventory_open:
                    if event.key == pg.K_q:
                        self.inventory_index -= 1
                        if self.inventory_index < 0:
                            self.inventory_index = len(self.inventory) - 1
                        self.gunmode = 0
                    if event.key == pg.K_e:
                        self.inventory_index += 1
                        self.inventory_index %= len(self.inventory)
                        self.gunmode = 0
            gundata = GUNDATA[self.inventory[self.inventory_index]]
            if 'modes' in gundata:
                for event in pg.event.get():
                    if event.type == pg.MOUSEWHEEL:
                        self.gunmode += event.y
                        self.gunmode %= len(gundata['modes'])
                gundata = gundata['modes'][self.gunmode]
            mouse_pos = [float(a) for a in pg.mouse.get_pos()]
            mouse_pos[0] /= WINTIMES; mouse_pos[1] /= WINTIMES
            angle = math.degrees(math.atan2(mouse_pos[1] - self.player_rect.centery, 
                                            mouse_pos[0] - self.player_rect.centerx))
            left = angle < -90 or angle > 90
            gun = gundata['image']
            if left: gun = pg.transform.flip(gun, False, True)
            gun = pg.transform.rotate(gun, -angle)
            playerx, playery = self.player_rect.center
            rect = gun.get_rect(center=(playerx, playery))
            direction = pg.Vector2(mouse_pos[0] - playerx, mouse_pos[1] - playery)
            try: direction = direction.normalize()
            except: direction = pg.Vector2(0, 0)
            rect.x += round(direction.x * 20); rect.y += round(direction.y * 20)
            if pg.mouse.get_pressed()[0] and self.shoot_timer.update() and not gundata['once_a_time']:
                self.shoot(gundata, angle, rect)
            for event in pg.event.get(pg.MOUSEBUTTONDOWN):
                if event.button == 1 and self.shoot_timer.update() and gundata['once_a_time']:
                    self.shoot(gundata, angle, rect)
            self.corspes.update(self, main)
            self.corspes.draw(main.surface)
            self.blood.update(self, main)
            self.blood.draw(main.surface)
            if gundata['laser']:
                pc = self.player_rect.center; x, y = pc
                vector = pg.Vector2(mouse_pos)-pg.Vector2(pc)
                linex, liney = vector.normalize()
                enemies = [sp.rect for sp in self.enemies]
                for _ in range(500):
                    x += linex; y += liney
                    col_rect = pg.Rect(x, y, 1, 1)
                    if not self.touched(col_rect): break
                    if col_rect.collidelist(enemies)!=-1: break
                    pg.draw.rect(main.surface,GREEN,col_rect)
            main.surface.blit(gun, rect)
            self.shoot_timer.duration = gundata['cooldown'] * 1000
            self.walls.update(self, main)
            self.bullets.update(self)
            self.particles.update(self, main)
            self.enemies.update(self, main)
            if self.tick_timer.update():
                for enemy in self.enemies:
                    enemy.update_movement(self, main)
            self.all_sprites.draw(main.surface)
            if self.flip:
                main.surface.blit(self.player_flip, self.player_rect)
            else: main.surface.blit(self.player_image, self.player_rect)

            # draw the health bar
            draw_text(f'Health: {self.player_health}', get_font(17), 
                    BLACK, main.surface, 7, 7, 'left')
            draw_text(f'FPS: {round(sum(self.fps_list)/len(self.fps_list))}', 
                      get_font(17), BLACK, main.surface, 7, 25, 'left')
            pg.draw.rect(main.surface, BLACK, (8, 18, PLAYERHEALTH*5 + 4, 9))
            pg.draw.rect(main.surface, LIGHTRED, (10, 20, self.player_health*5, 5))
            draw_text(self.inventory[self.inventory_index], get_font(30), 
                      BLACK, main.surface, WINSW//2, 20, 'center')
            draw_text(gundata['tooltip'], get_font(20), BLACK, 
                      main.surface, WINSW//2, 35, 'center')
            # print(self.fps_list)
        return self.player_health > 0
    
    def game_over(self, main):
        """Display the game over screen."""
        draw_text('GAME OVER', pg.font.SysFont(None, 100), BLACK, 
                  main.surface, WINSW//2, WINSH//2, 'center')
    
    def bomb(self, gundata:dict, angle, rect: pg.Rect):
        """Fire a grenade-type weapon and apply knockback."""
        self.shoot_timer.start_timer()
        Grenade([self.all_sprites, self.bullets], *rect.center, angle,
                gundata['bulletspeed'], gundata['damage'])
        gundata['sound'].play()
        x = math.cos(math.radians(angle)) * gundata['kickback']
        y = math.sin(math.radians(angle)) * gundata['kickback']
        self.player_knockback.x -= x; self.player_knockback.y -= y
    
    def shoot(self, gundata:dict, angle, rect:pg.Rect):
        """Shoot a bullet or grenade based on gun data."""
        if gundata.get('bomb', False):
            self.bomb(gundata, angle, rect)
        else:
            for _ in range(gundata['quantity']):
                angle += randint(-gundata['deviation'], gundata['deviation'])
                direction = pg.Vector2(
                    math.cos(math.radians(angle)), math.sin(math.radians(angle)))
                if not gundata['penetrative']:
                    Bullet([self.all_sprites, self.bullets], *rect.center, direction, angle, 
                        gundata['bulletspeed'], gundata['damage'], False)
                else: PBullet([self.all_sprites, self.bullets], *rect.center, direction, angle,
                            gundata['bulletspeed'], gundata['damage'], False)
            gundata['sound'].play()
            x = math.cos(math.radians(angle)) * gundata['kickback']
            y = math.sin(math.radians(angle)) * gundata['kickback']
            self.player_knockback.x -= x; self.player_knockback.y -= y
            self.shoot_timer.start_timer()

    def handle_inventory_ui(self, main):
        """Draw and handle the inventory UI for gun order adjustment."""
        if not hasattr(self, "open_surface"):
            self.open_surface = main.surface.copy()
        main.surface.blit(self.open_surface, (0, 0))
        # Draw inventory overlay
        overlay = pg.Surface(WINSURFACE, pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        main.surface.blit(overlay, (0, 0))
        font = get_font(32)
        draw_text("Inventory (I/Esc/right click to close, click to select/swap)", font, WHITE, main.surface, WINSW//2, 40, 'center')
        mouse_x, mouse_y = pg.mouse.get_pos()
        mouse_x = int(mouse_x) // WINTIMES
        mouse_y = int(mouse_y) // WINTIMES
        # Determine which gun is hovered
        hovered = None
        for idx in range(len(self.inventory)):
            rect_y = 80 + idx * 32
            rect_h = font.get_height()
            rect = pg.Rect(WINSW//2-150, rect_y - rect_h//2, 300, rect_h)
            if rect.collidepoint(mouse_x, mouse_y):
                hovered = idx
        # Draw inventory list
        for idx, gun in enumerate(self.inventory):
            color = YELLOW if idx == hovered else WHITE
            draw_text(f"{idx+1}. {gun}", font, color, main.surface, WINSW//2, 80 + idx*32, 'center')
        # Handle mouse and keyboard input
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE or event.key == pg.K_i:
                    self.inventory_open = False
                    if hasattr(self, "_swap_index"):
                        del self._swap_index
                    if hasattr(self, "open_surface"):
                        del self.open_surface
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1 and hovered is not None:
                    # Left click: select/swap
                    if not hasattr(self, "_swap_index"):
                        self._swap_index = hovered
                    else:
                        i, j = self._swap_index, hovered
                        self.inventory[i], self.inventory[j] = self.inventory[j], self.inventory[i]
                        del self._swap_index
                elif event.button == 3:
                    # Right click: close inventory
                    self.inventory_open = False
                    if hasattr(self, "_swap_index"):
                        del self._swap_index
        # Show swap selection
        if hasattr(self, "_swap_index"):
            idx = self._swap_index
            rect_y = 80 + idx * 32
            rect_h = font.get_height()
            pg.draw.rect(main.surface, RED, (WINSW//2-150, rect_y - rect_h//2, 300, rect_h), 2)