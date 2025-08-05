import threading
import socket
import json
import time
from constants import jsonable_to_rect, rect_to_jsonable  # Make sure these exist

class MultiplayerHandler:
    def __init__(self, username, is_server, ip, port=50007):
        self.players = {}  # username -> position
        self.bullets = []  # list of bullet objects
        self.enemies = []  # list of enemy objects
        self.lock = threading.Lock()
        self.username = username
        self.is_server = is_server
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(0.2)
        
        # NEW: Track client addresses for server replies
        self.client_addresses = {}  # username -> (ip, port)
        
        if is_server:
            # Bind to all interfaces for external access
            self.sock.bind(('', port))
        self.running = True
        self.last_sent_pos = None
        self.last_shot = None
        self.thread = threading.Thread(target=self.listen, daemon=True)
        self.thread.start()
        if is_server:
            self.broadcast_thread = threading.Thread(target=self.broadcast_loop, daemon=True)
            self.broadcast_thread.start()

    def listen(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                msg = json.loads(data.decode())
                
                if self.is_server:
                    # NEW: Record client address for future replies
                    uname = msg.get('username')
                    if uname:
                        with self.lock:
                            self.client_addresses[uname] = addr
                    
                    # Process player updates
                    if 'pos' in msg:
                        pos = tuple(msg['pos'])
                        with self.lock:
                            self.players[uname] = pos
                    if 'shoot' in msg:
                        with self.lock:
                            self.last_shot = (uname, msg['shoot'])

                else:
                    # Client receives game state from server
                    if 'players' in msg:
                        with self.lock:
                            self.players = {uname: tuple(pos) for uname, pos in msg['players'].items()}
                            self.bullets = [jsonable_to_rect(b) for b in msg.get('bullets', [])]
                            self.enemies = [jsonable_to_rect(e) for e in msg.get('enemies', [])]
                time.sleep(0.05)
            except socket.timeout:
                # Reduce timeout spam in console
                continue
            except Exception as e:
                # Print errors for debugging
                # print(f"Listen error: {e}")
                continue

    def broadcast_loop(self):
        while self.running:
            with self.lock:
                if not self.client_addresses:
                    time.sleep(0.1)
                    continue
                    
                # Prepare game state
                state = {
                    'players': self.players.copy(),
                    'bullets': [rect_to_jsonable(b) for b in self.bullets],
                    'enemies': [rect_to_jsonable(e) for e in self.enemies]
                }
                data = json.dumps(state).encode()
                
                # NEW: Send to all connected clients
                for addr in self.client_addresses.values():
                    try:
                        self.sock.sendto(data, addr)
                    except:
                        continue
            time.sleep(0.05)

    def add_player(self, username, pos):
        with self.lock:
            print("Lock acquired in add_player")
            self.players[username] = pos

    def remove_player(self, username):
        with self.lock:
            if username in self.players:
                del self.players[username]
            # NEW: Clean up address tracking
            if username in self.client_addresses:
                del self.client_addresses[username]

    def update_player(self, username, pos):
        with self.lock: 
            self.players[username] = pos
            
        msg = json.dumps({'username': username, 'pos': pos}).encode()
        
        if self.is_server:
            self.last_sent_pos = pos
        else:
            # Send directly to server
            self.sock.sendto(msg, (self.ip, self.port))

    def send_shoot(self, username, shoot_data):
        if not self.is_server:
            msg = json.dumps({'username': username, 'shoot': shoot_data}).encode()
            self.sock.sendto(msg, (self.ip, self.port))

    def get_players(self):
        with self.lock:
            # Include self in player list
            players = self.players.copy()
            players[self.username] = self.players.get(self.username, (0, 0))
            return players

    def get_bullets(self):
        with self.lock:
            return self.bullets.copy()

    def get_enemies(self):
        with self.lock:
            return self.enemies.copy()

    def stop(self):
        self.running = False
        self.sock.close()
        if self.is_server:
            self.broadcast_thread.join(timeout=0.1)
        self.thread.join(timeout=0.1)