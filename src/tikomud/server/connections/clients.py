from datetime import datetime
import threading

clients = {}
clients_lock = threading.Lock()

def add_client(conn, username: str) -> None:
    with clients_lock:
        clients[conn] = username

def remove_client(conn):
    with clients_lock:
        return clients.pop(conn, None)

def get_name(conn) -> str:
    with clients_lock: return clients.get(conn, "Unknown")

def broadcast(text: str, sender = "Server") -> None:
    sender_name = sender if isinstance(sender, str) else get_name(sender)
    line = f"{datetime.now().strftime('%H:%M:%S')} [{sender_name}]: {text}"

    with clients_lock:
        conns = list(clients.keys())

    for c in conns:
        try:
            c.sendall((line + "\n").encode("utf-8"))
        except OSError:
            pass
