import pygame as pg
from level import Level
from constants import *
from multiplayerhandler import MultiplayerHandler
pg.init()
pg.mixer.init()

class Main:
    def __init__(self) -> None:
        self.running = True
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode(WINSIZE)
        self.surface = pg.Surface(WINSURFACE)
        self.multiplayer = False
        self.username = None
        self.mphandler = None
        self.select_mode()

    def select_mode(self):
        import tkinter as tk
        from tkinter import simpledialog
        root = tk.Tk(); root.withdraw()
        mode = simpledialog.askstring("Mode", "Enter 'single', 'server', or 'client':")
        if mode == "server" or mode == "client":
            self.multiplayer = True
            # self.username = simpledialog.askstring("Username", "Enter your username:")
            # ip = simpledialog.askstring("IP", "Enter server IP (for server, use 0.0.0.0):")
            if mode == "client": self.username = 'client'
            else: self.username = 'server'
            ip = '127.0.0.1'
            is_server = (mode == "server")
            self.mphandler = MultiplayerHandler(self.username, is_server, ip)
            self.mphandler.add_player(self.username, PLAYERPOS)
            print("aaa")
        else:
            self.multiplayer = False
            self.username = "Player"
            self.mphandler = None

        self.level = Level(username=self.username, multiplayer=self.multiplayer, mphandler=self.mphandler)
        root.destroy()

    def run_game(self) -> None:
        alive = True
        while self.running:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
                pg.event.post(event)
            if alive: alive = self.level.update(self)
            else: self.level.game_over(self)
            surface = pg.transform.scale(self.surface, WINSIZE)
            self.screen.blit(surface, (0, 0))
            pg.display.flip()
        if self.mphandler:
            self.mphandler.stop()
        pg.quit()

if __name__ == '__main__':
    Main().run_game()