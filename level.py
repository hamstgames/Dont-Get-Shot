import pygame as pg
import json
from constants import *
from sprites import *

class Level:
    """Main game level logic, including player, enemies, inventory, and update loop."""
    def __init__(self, username: Union[None,str]="Player", multiplayer=False, mphandler=None) -> None:
        """Initialize the level, player, enemies, and inventory."""
        self.player_image = IMAGES['player']
        self.player_flip = pg.transform.flip(self.player_image, True, False)
        self.player_rect:pg.Rect = self.player_image.get_rect(center=PLAYERPOS)
        self.player_world_pos = [0, 0]
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
        self.inventory = ['Budget Revolver','High Caliber Pistol','AK - 47','Regular Shotgun',
                          'M(16)op Gun','Kriss SuperV','MP - 5','Grenade Launcher','UZI','B - 25',
                          'Big & Heavy','Double Barrel','Trash 5Run','Sniper Rifle','Golden Pistol']
        self.inventory_index = 0; self.gunmode = 0
        if multiplayer == False or mphandler.is_server: # pyright: ignore[reportOptionalMemberAccess]
            # only create enemies if this is the server
            Enemy([self.all_sprites, self.enemies], 150, 50, IMAGES['enemy'], 1)
        self.tick_timer = PulseTimer(1000 / TPS)
        self.debug = True
        self.player_knockback = pg.Vector2(0, 0)
        self.fps_list = []
        self.inventory_open = False
        self.inventory_selected = 0
        self.username = username
        self.multiplayer = multiplayer
        self.mphandler = mphandler

    def touched(self, rect: Optional[pg.Rect] = None) -> bool:
        """Check if the given rect collides with any touchable object."""
        rect = self.player_rect if rect is None else rect
        collist = list(self.touchable)
        collisions = rect.collidelist(collist)
        return collisions == -1

    def update(self, main: Any, dt) -> bool:
        """Update the game state or show inventory if open."""
        if self.inventory_open:
            self.handle_inventory_ui(main)
        else:
            fps = main.clock.get_fps()
            self.fps_list.append(fps)
            if len(self.fps_list) > 10: self.fps_list.pop(0)
            dt = round(dt * 60 / 1000, 2)
            main.surface.fill(GRAY)
            keys = pg.key.get_pressed()
            self.movex, self.movey = 0, 0
            if keys[pg.K_a]:
                self.player_rect.x -= PLAYERSPEED * dt
                if self.touched(): self.movex = PLAYERSPEED * dt; self.flip = False
                self.player_rect.x += PLAYERSPEED * dt
            if keys[pg.K_d]:
                self.player_rect.x += PLAYERSPEED * dt
                if self.touched(): self.movex = -PLAYERSPEED * dt; self.flip = True
                self.player_rect.x -= PLAYERSPEED * dt
            if keys[pg.K_w]:
                self.player_rect.y -= PLAYERSPEED * dt
                if self.touched(): self.movey = PLAYERSPEED * dt
                self.player_rect.y += PLAYERSPEED * dt
            if keys[pg.K_s]:
                self.player_rect.y += PLAYERSPEED * dt
                if self.touched(): self.movey = -PLAYERSPEED * dt
                self.player_rect.y -= PLAYERSPEED * dt
            vector = pg.Vector2(self.movex, self.movey)
            if vector: vector.normalize_ip()
            self.movex = vector.x * PLAYERSPEED * dt; self.movey = vector.y * PLAYERSPEED * dt
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
            self.player_world_pos[0] -= round(self.movex)
            self.player_world_pos[1] -= round(self.movey)
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
            self.bullets.update(self, dt)
            self.particles.update(self, main)
            self.enemies.update(self, main, dt)
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
            draw_text(f'dt: {dt}', get_font(17),
                      BLACK, main.surface, 7, 43, 'left')
            pg.draw.rect(main.surface, BLACK, (8, 18, PLAYERHEALTH*5 + 4, 9))
            pg.draw.rect(main.surface, LIGHTRED, (10, 20, self.player_health*5, 5))
            draw_text(self.inventory[self.inventory_index], get_font(30), 
                      BLACK, main.surface, WINSW//2, 20, 'center')
            draw_text(gundata['tooltip'], get_font(20), BLACK, 
                      main.surface, WINSW//2, 35, 'center')
            if self.multiplayer and self.mphandler:
                self.mphandler.update_player(self.username, self.player_world_pos)
                if self.mphandler.is_server:
                    # Server: update all players, bullets, enemies
                    bullets_data = wpos_by_spos_all(self.bullets,self.player_world_pos)
                    self.mphandler.bullets = bullets_data
                    enemies_data = wpos_by_spos_all(self.enemies,self.player_world_pos)
                    self.mphandler.enemies = enemies_data
                    
                    # Send updated game state to all clients
                    state_msg = {
                        'players': self.mphandler.players.copy(),
                        'bullets': bullets_data,
                        'enemies': enemies_data
                    }
                    msg = json.dumps(state_msg).encode()
                    
                    # Send to all connected clients
                    for addr in self.mphandler.client_addresses.values():
                        try:
                            self.mphandler.sock.sendto(msg, addr)
                        except:
                            continue
                    
                    if self.mphandler.last_shot:
                        uname, shoot_data = self.mphandler.last_shot
                        if uname != self.username:
                            self.create_bullet_for_player(uname, shoot_data)
                        self.mphandler.last_shot = None

                    # Draw all players except self
                    for uname, pos in self.mphandler.get_players().items():
                        if uname == self.username or pos is None: continue
                        adj_pos = self.adjust_pos(pos)
                        pg.draw.circle(main.surface, BLUE, adj_pos, 25)
                        draw_text(uname, get_font(18), BLACK, main.surface, adj_pos[0], adj_pos[1]-30, 'center')
                    # Draw all bullets
                    for b in self.mphandler.get_bullets():
                        adj_pos = self.adjust_pos((b[0], b[1]))
                        pg.draw.circle(main.surface, RED, adj_pos, 5)
                    # Draw all enemies
                    for e in self.mphandler.get_enemies():
                        adj_pos = self.adjust_pos((e[0], e[1]))
                        pg.draw.rect(main.surface, GREEN, (adj_pos[0]-15, adj_pos[1]-15, 30, 30))
                else:
                    # Client: update own player, send position and shoot requests
                    # Draw other players
                    for uname, pos in self.mphandler.get_players().items():
                        if uname == self.username or pos is None: continue
                        adj_pos = self.adjust_pos(pos)
                        pg.draw.circle(main.surface, BLUE, adj_pos, 25)
                        draw_text(uname, get_font(18), BLACK, main.surface, adj_pos[0], adj_pos[1]-30, 'center')
                    # Draw bullets received from server
                    for b in self.mphandler.get_bullets():
                        adj_pos = self.adjust_pos((b[0], b[1]))
                        pg.draw.circle(main.surface, RED, adj_pos, 5)
                    # Draw enemies received from server
                    for e in self.mphandler.get_enemies():
                        adj_pos = self.adjust_pos((e[0], e[1]))
                        pg.draw.rect(main.surface, GREEN, (adj_pos[0]-15, adj_pos[1]-15, 30, 30))
                    # Draw own username above player sprite
                    draw_text(self.username, get_font(18), BLACK, main.surface, self.player_rect.centerx, self.player_rect.centery-30, 'center')
        return self.player_health > 0
    
    def adjust_pos(self, pos):
        return [
            pos[0] + PLAYERPOS[0] - self.player_world_pos[0],
            pos[1] + PLAYERPOS[1] - self.player_world_pos[1]
        ]
    
    def create_bullet_for_player(self, uname: str, shoot_data: dict) -> None:
        """Create a bullet for a player based on the received shoot data."""
        player_pos = self.mphandler.get_players().get(uname)  # type: ignore
        if not player_pos: return
        # Calculate actual bullet position
        gun_offset_x = shoot_data['rect'][0] - PLAYERPOS[0]
        gun_offset_y = shoot_data['rect'][1] - PLAYERPOS[1]
        bullet_x = player_pos[0] + gun_offset_x
        bullet_y = player_pos[1] + gun_offset_y
        
        # Get gun data
        gun_name = shoot_data['gun']
        gundata = GUNDATA[gun_name]
        if 'modes' in gundata:
            gundata = gundata['modes'][0]  # Use first mode
        
        # Create bullet
        direction = pg.Vector2(
            math.cos(math.radians(shoot_data['angle'])),
            math.sin(math.radians(shoot_data['angle']))
        )
        Bullet([self.all_sprites, self.bullets], 
               bullet_x, bullet_y, 
               direction, shoot_data['angle'],
               gundata['bulletspeed'], gundata['damage'], False)

    def game_over(self, main: Any) -> None:
        """Display the game over screen."""
        draw_text('GAME OVER', pg.font.SysFont(None, 100), BLACK, 
                  main.surface, WINSW//2, WINSH//2, 'center')
    
    def bomb(self, gundata: dict, angle: float, rect: pg.Rect) -> None:
        """Fire a grenade-type weapon and apply knockback."""
        self.shoot_timer.start_timer()
        Grenade([self.all_sprites, self.bullets], *rect.center, angle,
                gundata['bulletspeed'], gundata['damage'])
        gundata['sound'].play()
        x = math.cos(math.radians(angle)) * gundata['kickback']
        y = math.sin(math.radians(angle)) * gundata['kickback']
        self.player_knockback.x -= x; self.player_knockback.y -= y
    
    def shoot(self, gundata: dict, angle: float, rect: pg.Rect) -> None:
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

    def handle_inventory_ui(self, main: Any) -> None:
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