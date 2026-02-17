from datetime import datetime
import threading

from tikomud.server.game.player import Player

clients = {}
clients_lock = threading.Lock()

def add_client(conn, player: Player) -> None:
    with clients_lock:
        clients[conn] = player

def remove_client(conn):
    with clients_lock:
        return clients.pop(conn, None)

def get_name(conn) -> str:
    with clients_lock:
        player = clients.get(conn)
        return player.name if player else "Unknown"

def broadcast(text: str, sender = "Server") -> None:
    sender_name = sender.name if isinstance(sender, Player) else sender
    line = f"{datetime.now().strftime('%H:%M:%S')} [{sender_name}]: {text}"

    with clients_lock:
        conns = list(clients.keys())

    for c in conns:
        try:
            c.sendall((line + "\n").encode("utf-8"))
        except OSError:
            pass
