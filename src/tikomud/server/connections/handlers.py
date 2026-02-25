import json

from tikomud.server.connections.clients import add_client, remove_client, broadcast_json, kicked
from tikomud.server.game.game import Game
from tikomud.server.game.player import Player
from tikomud.server.connections.dispatch import handle_command

# Handles a single client connection.
# Responsible for player registration, receiving messages, and dispatching commands.
def handle_client(game: Game, conn, buff_size: int) -> None:
    username = ""

    try:
        # Receive initial data from client (expected to be the username).
        data = conn.recv(buff_size)
        if not data:
            return

        username = data.decode("utf-8", errors="replace").strip()
        if not username:
            return

        # Create new player instance and add to server/client tracking.
        new_player = Player(username)
        add_client(conn, new_player)
        game.add_player(new_player)

        # Set starting location in the game world.
        start_map_name = "overworld"
        start_room_id = "room1"

        start_map = game.world[start_map_name]
        start_room = start_map.get_room(start_room_id)

        start_room.add_player(new_player)
        new_player.set_position(start_map_name, start_room_id)

        print(f"{username} joined.")

        # Notify all clients that a new player has joined.
        broadcast_json(
            {
                "type": "system",
                "message": f"{username} joined!",
            }
        )

        buffer = ""

        # Main loop: receive and process client messages.
        while True:
            data = conn.recv(buff_size)
            if not data:
                print(f"{username} disconnected.")
                break

            buffer += data.decode("utf-8", errors="replace")

            # Process complete lines of JSON messages.
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.rstrip("\r").strip()
                if not line:
                    continue

                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    # Respond to client with JSON error if message is invalid.
                    try:
                        conn.sendall(
                            (json.dumps({"type": "error", "code": "INVALID_JSON", "message": "Invalid JSON"}) + "\n").encode("utf-8")
                        )
                    except OSError:
                        pass
                    continue

                # Dispatch validated command to server logic.
                handle_command(game=game, conn=conn, player=new_player, msg=msg)

    except ConnectionResetError:
        print(f"Connection reset by {username or 'unknown'}.")
    finally:
        # Remove client from server tracking on disconnect.
        leaving = remove_client(conn)

        if leaving:
            if leaving in game.players:
                game.remove_player(leaving)
                # Check if the player was kicked or left voluntarily.
                if leaving.name in kicked:
                    kicked.remove(leaving.name)
                    print(f"{leaving.name} was kicked.")
                    broadcast_json({"type": "system", "message": f"{leaving.name} was kicked by the server!"})
                else:
                    print(f"{leaving.name} left.")
                    broadcast_json({"type": "system", "message": f"{leaving.name} has left!"})

        # Ensure socket is closed cleanly.
        try:
            conn.close()
        except OSError:
            pass
