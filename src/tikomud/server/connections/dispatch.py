from tikomud.server.connections.clients import broadcast_chat
from tikomud.server.connections.clients import send_json_to

# Dispatches incoming commands from a client to the appropriate server/game logic.
# Handles parsing, validation, and sending responses back to the client.
def handle_command(game, conn, player, msg: dict) -> None:
    # Ensure the message is a dictionary.
    if not isinstance(msg, dict):
        return

    # Only process messages of type 'command'.
    if msg.get("type") != "command":
        return

    command = msg.get("command")
    payload = msg.get("payload", {})

    # Handle the "yell" command: broadcast a message to all connected players.
    if command == "yell":
        message = ""
        if isinstance(payload, dict):
            message = str(payload.get("message", "")).strip()

        if not message:
            return

        broadcast_chat(message, sender=player)
        return

    # Handle the "inv" command: send the player's inventory as a system message.
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

    # Handle the "move" command: attempt to move the player in the specified direction.
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
