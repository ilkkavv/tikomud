from tikomud.server.connections.clients import broadcast_chat

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
