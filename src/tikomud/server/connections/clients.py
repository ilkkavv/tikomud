from datetime import datetime
import threading
import socket

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

# Add kick command to server to remove unwanted players.
def kick_by_name(name: str) -> bool:
    name = name.strip().lower()
    target_conn = None

    # First: find and remove under lock
    with clients_lock:
        for conn, player in list(clients.items()):
            if player.name.lower() == name:
                target_conn = conn
                clients.pop(conn, None)
                break

    if not target_conn:
        return False

    # Now operate on socket OUTSIDE the lock
    try:
        target_conn.sendall(b"You have been kicked by the server.\n")
    except OSError:
        pass

    try:
        target_conn.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass

    try:
        target_conn.close()
    except OSError:
        pass

    return True
