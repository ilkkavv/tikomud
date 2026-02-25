from tikomud.server.connections.clients import broadcast_chat
from tikomud.server.connections.clients import send_json_to

def handle_command(game, conn, player, msg: dict) -> None:
    if not isinstance(msg, dict):
        return

    if msg.get("type") != "command":
        return

    command = msg.get("command")
    payload = msg.get("payload", {})

    if command == "yell":
        message = ""
        if isinstance(payload, dict):
            message = str(payload.get("message", "")).strip()

        if not message:
            return

        broadcast_chat(message, sender=player)
        return

    if command == "inv":
        lines = player.list_inventory()
        text = "Inventory: " + ", ".join(lines)

        send_json_to(
            conn,
            {
                "type": "system",
                "message": text,
            },
        )
        return

    if command == "move":
        direction = str(payload.get("dir", "")).lower()

        success, message = game.move_player(player, direction)

        send_json_to(
            conn,
            {
                "type": "system",
                "message": message,
            },
        )
        return
