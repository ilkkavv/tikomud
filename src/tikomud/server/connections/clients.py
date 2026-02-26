from datetime import datetime
import threading
import socket
import json

from tikomud.server.game.player import Player

clients = {}
clients_lock = threading.Lock()
kicked = set()

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

def _send_json(conn, obj: dict) -> None:
    line = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    conn.sendall(line.encode("utf-8"))

def send_json_to(conn, obj: dict) -> None:
    try:
        _send_json(conn, obj)
    except OSError:
        pass

def broadcast_json(obj: dict) -> None:
    with clients_lock:
        conns = list(clients.keys())

    for c in conns:
        try:
            _send_json(c, obj)
        except OSError:
            pass

def broadcast_chat(message: str, sender="Server") -> None:
    sender_name = sender.name if isinstance(sender, Player) else str(sender)
    payload = {
        "type": "chat",
        "time": datetime.now().strftime("%H:%M:%S"),
        "sender": sender_name,
        "message": message,
    }
    broadcast_json(payload)

def broadcast_chat_in_room(message: str, sender: Player) -> None:
    sender_room = sender.position.get("room")
    sender_name = sender.name

    payload = {
        "type": "chat",
        "time": datetime.now().strftime("%H:%M:%S"),
        "sender": sender_name,
        "message": message,
    }

    with clients_lock:
        items = list(clients.items())

    for conn, player in items:
        if player.position.get("room") == sender_room:
            try:
                _send_json(conn, payload)
            except OSError:
                pass

def kick_by_name(name: str) -> bool:
    name = name.strip().lower()
    target_conn = None
    target_player = None

    with clients_lock:
        for conn, player in clients.items():
            if player.name.lower() == name:
                target_conn = conn
                target_player = player
                kicked.add(player.name)
                break

    if not target_conn:
        return False

    try:
        _send_json(target_conn, {"type": "system", "message": "You have been kicked by admin."})
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
