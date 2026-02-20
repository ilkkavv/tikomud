from tikomud.server.connections.clients import add_client, remove_client, broadcast, kicked
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
            if raw.lower() in ("inv", "inventory"):
                lines = new_player.list_inventory()
                text = "\n".join(lines) + "\n"
                conn.sendall(text.encode("utf-8"))
                continue

            broadcast(raw, new_player)
    except ConnectionResetError:
        print(f"Connection reset by {username or 'unknown'}.")
    finally:
        leaving = remove_client(conn)

        if leaving:
            if leaving in game.players:
                game.remove_player(leaving)
                if leaving.name in kicked:
                    kicked.remove(leaving.name)
                    print(f"{leaving.name} was kicked.")
                    broadcast(f"{leaving.name} was kicked by the server!")
                else:
                    print(f"{leaving.name} left.")
                    broadcast(f"{leaving.name} has left!")

        try:
            conn.close()
        except OSError:
            pass
