from tikomud.server.connections.handlers import handle_client
from tikomud.server.connections.clients import kick_by_name
from tikomud.server.game.game import Game

import socket
import threading

# Entry point for running the TIKOMUD server.
# Sets up the game, network socket, and threads for handling clients and admin commands.
def run(host: str = "127.0.0.1", port: int = 7537, max_clients: int = 10, buff_size: int = 1024) -> None:
    print("Starting TIKOMUD server...")

    # Initialize the game instance.
    game = Game()

    # Create and configure TCP socket for incoming connections.
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.bind((host, port))
    tcp_socket.listen(max_clients)

    print(f"Server is running at {host}:{port}")
    print("Waiting for connections...")

    # Start a separate daemon thread for the admin console.
    threading.Thread(target=admin_console, daemon=True).start()

    # Main loop: accept and handle incoming client connections.
    while True:
        conn, addr = tcp_socket.accept()
        print(f"New connection from {addr}")
        t = threading.Thread(target=handle_client, args=(game, conn, buff_size), daemon=True)
        t.start()

# Simple admin console for server-side commands.
# Currently supports kicking players by name.
def admin_console():
    while True:
        cmd = input()
        if cmd.startswith("kick "):
            name = cmd.split(" ", 1)[1]
            if kick_by_name(name):
                print(f"{name} was kicked.")
            else:
                print(f"No player named {name}.")
