from tikomud.server.connections.clients import add_client, remove_client, broadcast
from tikomud.server.game.game import Game
from tikomud.server.game.player import Player

def handle_client(game: Game, conn, buff_size: int) -> None:
    username = ""

    try:
        data = conn.recv(buff_size)
        if not data:
            return

        username = data.decode("utf-8", errors="replace").strip()

        if not username:
            return

        new_player = Player(username)
        add_client(conn, new_player)
        game.add_player(new_player)
        print(f"{username} joined.")

        broadcast(f"{username} joined!")

        while True:
            data = conn.recv(buff_size)
            if not data:
                print(f"{username} disconnected.")
                break

            raw = data.decode("utf-8", errors="replace").strip()
            if not raw:
                continue

            broadcast(raw, new_player)
    except ConnectionResetError:
        print(f"Connection reset by {username or 'unknown'}.")
    finally:
        leaving = remove_client(conn)

        if leaving:
            if leaving in game.players:
                game.remove_player(leaving)
            print(f"{leaving.name} left.")
            broadcast(f"{leaving.name} has left!")

        try:
            conn.close()
        except OSError:
            pass
