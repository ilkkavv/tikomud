from datetime import datetime
import threading
import socket
import json

from tikomud.server.game.player import Player

# Module for managing connected clients and communication in the MUD server.
# Provides functions to add/remove clients, send JSON messages, broadcast chat, and handle kicks.

clients = {}  # Maps socket connections to Player instances.
clients_lock = threading.Lock()  # Ensures thread-safe access to the clients dictionary.
kicked = set()  # Tracks names of players who were kicked.

# Add a new client to the server tracking.
def add_client(conn, player: Player) -> None:
    with clients_lock:
        clients[conn] = player

# Remove a client from server tracking.
def remove_client(conn):
    with clients_lock:
        return clients.pop(conn, None)

# Retrieve a player's name from a connection.
def get_name(conn) -> str:
    with clients_lock:
        player = clients.get(conn)
        return player.name if player else "Unknown"

# Low-level helper to send a JSON object to a connection.
def _send_json(conn, obj: dict) -> None:
    line = json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n"
    conn.sendall(line.encode("utf-8"))

# Safely send a JSON object to a client connection.
def send_json_to(conn, obj: dict) -> None:
    try:
        _send_json(conn, obj)
    except OSError:
        pass

# Broadcast a JSON object to all connected clients.
def broadcast_json(obj: dict) -> None:
    with clients_lock:
        conns = list(clients.keys())

    for c in conns:
        try:
            _send_json(c, obj)
        except OSError:
            pass

# Broadcast a chat message to all clients, including timestamp and sender info.
def broadcast_chat(message: str, sender="Server") -> None:
    sender_name = sender.name if isinstance(sender, Player) else str(sender)
    payload = {
        "type": "chat",
        "time": datetime.now().strftime("%H:%M:%S"),
        "sender": sender_name,
        "message": message,
    }
    broadcast_json(payload)

# Kick a player by name: sends a system message, closes their connection, and removes them from tracking.
def kick_by_name(name: str) -> bool:
    name = name.strip().lower()
    target_conn = None
    target_player = None

    # Find the target player connection.
    with clients_lock:
        for conn, player in clients.items():
            if player.name.lower() == name:
                target_conn = conn
                target_player = player
                kicked.add(player.name)
                break

    if not target_conn:
        return False

    # Notify the client they were kicked.
    try:
        _send_json(target_conn, {"type": "system", "message": "You have been kicked by admin."})
    except OSError:
        pass

    # Shut down and close the socket cleanly.
    try:
        target_conn.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass

    try:
        target_conn.close()
    except OSError:
        pass

    return True
