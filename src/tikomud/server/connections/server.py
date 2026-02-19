from tikomud.server.connections.handlers import handle_client
from tikomud.server.connections.clients import kick_by_name
from tikomud.server.game.game import Game

import socket
import threading

def run(host: str = "127.0.0.1", port: int = 7537, max_clients: int = 10, buff_size: int = 1024) -> None:
    print("Starting TIKOMUD server...")

    game = Game()

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.bind((host, port))
    tcp_socket.listen(max_clients)

    print(f"Server is running at {host}:{port}")
    print("Waiting for connections...")

    # Starts admin console thread.
    threading.Thread(target=admin_console, daemon=True).start()

    while True:
        conn, addr = tcp_socket.accept()
        print(f"New connection from {addr}")
        t = threading.Thread(target=handle_client, args=(game, conn, buff_size), daemon=True)
        t.start()

def admin_console():
    while True:
        cmd = input()
        if cmd.startswith("kick "):
            name = cmd.split(" ", 1)[1]
            if kick_by_name(name):
                print(f"{name} was kicked.")
            else:
                print(f"No player named {name}.")
