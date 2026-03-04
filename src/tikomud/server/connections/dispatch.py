from tikomud.server.connections.clients import broadcast_chat, broadcast_chat_in_room
from tikomud.server.connections.clients import send_json_to


def _parse_name_qty_from_payload(payload: dict) -> tuple[int, str]:
    # Extract item name and quantity safely from command payload
    item_name = str(payload.get("item", "")).strip()
    qty = payload.get("qty", 1)

    try:
        qty = int(qty)
    except (TypeError, ValueError):
        qty = 1

    # Ensure quantity is always at least 1
    qty = max(1, qty)
    return qty, item_name


def build_dialogue_text(node: dict) -> str:
    if not node:
        return ""

    text = node.get("text", "")
    options = node.get("options", [])

    if not options:
        return text

    lines = [text, ""]

    for i, option in enumerate(options):
        lines.append(f"{i+1}. {option.get('text','')}")

    lines.append("")
    lines.append("Choose a number.")

    return "\n".join(lines)


def handle_command(game, conn, player, msg: dict) -> None:
    # Main dispatcher for handling player commands

    if not isinstance(msg, dict):
        return

    if msg.get("type") != "command":
        return

    command = msg.get("command")
    payload = msg.get("payload", {})

    if command == "yell":
        # Global chat visible to all players
        message = ""
        if isinstance(payload, dict):
            message = str(payload.get("message", "")).strip()

        if not message:
            return

        broadcast_chat(message, sender=player)
        return

    # Chat only inside current room
    if command == "say":
        message = ""
        if isinstance(payload, dict):
            message = str(payload.get("message", "")).strip()

        if not message:
            return

        broadcast_chat_in_room(message, sender=player)
        return

    if command == "inv":
        # Return player's inventory contents
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
        # Move player in specified direction
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

    # Take item from current room
    if command == "take":
        qty, item_name = _parse_name_qty_from_payload(payload)

        if not item_name:
            send_json_to(
                conn,
                {
                    "type": "take",
                    "ok": False,
                    "message": "Usage: take <item> [qty]",
                },
            )
            return

        # Fetch current room
        map_name = player.position["map_name"]
        room_id = player.position["room"]

        if not map_name or not room_id:
            send_json_to(
                conn,
                {
                    "type": "take",
                    "ok": False,
                    "message": "Player position is unknown.",
                },
            )
            return

        # Get current room object
        game_map = game.world.get(map_name)
        if not game_map:
            send_json_to(
                conn,
                {
                    "type": "take",
                    "ok": False,
                    "message": "Current map not found.",
                },
            )
            return

        room_obj = game_map.get_room(room_id)
        if not room_obj:
            send_json_to(
                conn,
                {
                    "type": "take",
                    "ok": False,
                    "message": "Current room not found.",
                },
            )
            return

        # Resolve key in room items (support both key and display name)
        key = room_obj._resolve_key(item_name)
        if not key:
            send_json_to(
                conn,
                {
                    "type": "take",
                    "ok": False,
                    "message": f"'{item_name}' is not in this room.",
                },
            )
            return

        # Read item info via Room API (thread-safe)
        info = room_obj.get_item_info(key)
        if not info:
            send_json_to(
                conn,
                {
                    "type": "take",
                    "ok": False,
                    "message": f"'{item_name}' is not in this room.",
                },
            )
            return

        display_name, _available_qty, description = info

        # Attempt to remove the specified quantity from the room
        success = room_obj.remove_item(key, qty)
        if not success:
            send_json_to(
                conn,
                {
                    "type": "take",
                    "ok": False,
                    "message": f"Cannot take '{item_name}' x{qty} from the room.",
                },
            )
            return

        # Add item to player's inventory
        player.add_item(key, display_name, qty, description)

        # Notify all players in room about the pickup
        broadcast_chat_in_room(f"{player.name} picks up {display_name} x{qty}", sender=player)

        # Respond to the player
        send_json_to(
            conn,
            {
                "type": "take",
                "ok": True,
                "item": {
                    "key": key,
                    "name": display_name,
                    "quantity": qty,
                },
            },
        )
        return

    # Examine item from inventory
    if command == "examine":
        item_name = str(payload.get("item", "")).strip()

        if not item_name:
            send_json_to(
                conn,
                {
                    "type": "system",
                    "message": "Usage: examine <item>",
                },
            )
            return

        key = player._resolve_key(item_name)
        if not key:
            send_json_to(
                conn,
                {
                    "type": "system",
                    "message": f"'{item_name}' not found in your inventory.",
                },
            )
            return

        name, qty, desc = player.inventory[key]

        send_json_to(
            conn,
            {
                "type": "examine",
                "item": {
                    "key": key,
                    "name": name,
                    "quantity": qty,
                    "description": desc,
                },
            },
        )
        return

    if command == "drop":
        # Drop item from inventory into current room
        qty, item_name = _parse_name_qty_from_payload(payload)

        if not item_name:
            send_json_to(
                conn,
                {
                    "type": "error",
                    "message": "Usage: drop <item> [qty]",
                },
            )
            return

        if not player.has_item(item_name, qty):
            send_json_to(
                conn,
                {
                    "type": "drop",
                    "ok": False,
                    "message": f"You don't have '{item_name}' x{qty}.",
                },
            )
            return

        resolved_key = player._resolve_key(item_name)
        display_name, have, description = player.inventory[resolved_key]

        if not player.remove_item(item_name, qty):
            send_json_to(
                conn,
                {
                    "type": "drop",
                    "ok": False,
                    "message": "Failed to update ypur inventory.",
                },
            )
            return

        map_name = player.position["map_name"]
        room_id = player.position["room"]

        game.add_item_to_room(map_name, room_id, resolved_key, display_name, qty, description)

        # NOTE: this is global chat in your original code; keep as-is.
        broadcast_chat(f"{player.name} drops {display_name} x{qty}", sender=player)

        send_json_to(
            conn,
            {
                "type": "drop",
                "ok": True,
                "item": {
                    "key": resolved_key,
                    "name": display_name,
                    "quantity": qty,
                },
            },
        )
        return

    if command == "look":
        # Show current room information and floor items
        map_name = player.position.get("map_name")
        room_id = player.position.get("room")

        try:
            items = game.list_items_in_room(map_name, room_id)
        except Exception:
            items = []

        try:
            npcs = game.list_npcs_in_room(map_name, room_id)
            npc_names = [npc.name for npc in npcs]
        except Exception:
            npc_names = []

        send_json_to(
            conn,
            {
                "type": "look",
                "message": f"You are in {map_name}/{room_id}",
                "room": {"map": map_name, "id": room_id},
                "floor": items,
                "npcs": npc_names,
            },
        )
        return

    # Command talk
    if command == "talk":
        target = str(payload.get("target", "")).strip()

        # Case 1: Continue existing dialogue with numeric choice
        if player.active_npc and target.isdigit():
            choice_index = int(target) - 1

            npc = player.active_npc
            node = npc.dialogue.get(player.dialogue_node, {})
            options = node.get("options", [])

            if choice_index < 0 or choice_index >= len(options):
                send_json_to(
                    conn,
                    {
                        "type": "system",
                        "message": "Invalid choice.",
                    },
                )
                return

            next_id = options[choice_index]["next"]

            if next_id is None:
                player.active_npc = None
                player.dialogue_node = None
                send_json_to(
                    conn,
                    {
                        "type": "system",
                        "message": "Conversation ended.",
                    },
                )
                return

            player.dialogue_node = next_id
            next_node = npc.dialogue[next_id]

            send_json_to(
                conn,
                {
                    "type": "npc_talk",
                    "npc": npc.name,
                    "message": build_dialogue_text(next_node),
                },
            )
            return

        # Case 2: Start new dialogue
        if not target:
            send_json_to(
                conn,
                {
                    "type": "system",
                    "message": "Usage: talk <npc>",
                },
            )
            return

        map_name = player.position["map_name"]
        room_id = player.position["room"]

        npc = game.find_npc_in_room(map_name, room_id, target)

        if not npc:
            send_json_to(
                conn,
                {
                    "type": "system",
                    "message": f"There is no '{target}' here.",
                },
            )
            return

        if not npc.dialogue:
            send_json_to(
                conn,
                {
                    "type": "system",
                    "message": f"{npc.name} has nothing to say.",
                },
            )
            return

        # Initialize dialogue
        player.active_npc = npc
        player.dialogue_node = "start"

        start_node = npc.dialogue["start"]

        send_json_to(
            conn,
            {
                "type": "npc_talk",
                "npc": npc.name,
                "message": build_dialogue_text(start_node),
            },
        )
        return

    if command == "help":
        # Return list of available commands
        send_json_to(
            conn,
            {
                "type": "help",
                "commands": [
                    "help",
                    "inv",
                    "examine <item>",
                    "look",
                    "take <item> [qty]",
                    "drop <item> [qty]",
                    "yell <message>",
                ],
            },
        )
        return
