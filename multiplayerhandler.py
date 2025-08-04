import threading
import socket
import json

class MultiplayerHandler:
    def __init__(self, username, is_server, ip, port=50007):
        self.players = {}  # username -> position
        self.lock = threading.Lock()
        self.username = username
        self.is_server = is_server
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.settimeout(0.1)
        if is_server:
            self.sock.bind((ip, port))
        self.running = True
        self.last_sent_pos = None
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
                print(f"Received message from {addr}: {msg}")
                if self.is_server:
                    # Server receives client position, updates, and rebroadcasts all positions
                    uname = msg['username']
                    pos = tuple(msg['pos'])
                    with self.lock:
                        self.players[uname] = pos
                else:
                    # Client receives all positions from server
                    if 'players' in msg:
                        with self.lock:
                            self.players = {uname: tuple(pos) for uname, pos in msg['players'].items()}
            except socket.timeout:
                continue
            except Exception:
                continue

    def broadcast_loop(self):
        # Server: rebroadcast all positions every 50ms
        import time
        while self.running:
            with self.lock:
                # Always include own position
                self.players[self.username] = self.last_sent_pos if self.last_sent_pos else (0, 0)
                msg = json.dumps({'players': self.players})
            self.sock.sendto(msg.encode(), ('<broadcast>', self.port))
            time.sleep(0.05)

    def add_player(self, username, pos):
        with self.lock:
            self.players[username] = pos

    def remove_player(self, username):
        with self.lock:
            if username in self.players:
                del self.players[username]

    def update_player(self, username, pos):
        if self.is_server:
            # Server just updates its own position
            with self.lock:
                self.players[username] = pos
            self.last_sent_pos = pos
        else:
            # Client sends its position to server
            msg = json.dumps({'username': username, 'pos': pos})
            self.sock.sendto(msg.encode(), (self.ip, self.port))

    def get_players(self):
        with self.lock:
            # Always include our own position for rendering
            players = dict(self.players)
            players[self.username] = self.players.get(self.username, None)
            return players

    def stop(self):
        self.running = False
        self.sock.close()
