import json

from tikomud.server.connections.clients import add_client, remove_client, broadcast_json, kicked
from tikomud.server.game.game import Game
from tikomud.server.game.player import Player
from tikomud.server.connections.dispatch import handle_command

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

        broadcast_json(
            {
                "type": "system",
                "message": f"{username} joined!",
            }
        )

        buffer = ""

        while True:
            data = conn.recv(buff_size)
            if not data:
                print(f"{username} disconnected.")
                break

            buffer += data.decode("utf-8", errors="replace")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.rstrip("\r").strip()
                if not line:
                    continue

                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    try:
                        conn.sendall(
                            (json.dumps({"type": "error", "code": "INVALID_JSON", "message": "Invalid JSON"}) + "\n").encode("utf-8")
                        )
                    except OSError:
                        pass
                    continue

                handle_command(game=game, conn=conn, player=new_player, msg=msg)

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
                    broadcast_json({"type": "system", "message": f"{leaving.name} was kicked by the server!"})
                else:
                    print(f"{leaving.name} left.")
                    broadcast_json({"type": "system", "message": f"{leaving.name} has left!"})

        try:
            conn.close()
        except OSError:
            pass
