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
            send_json_to(conn, {
                "type": "error",
                "message": "Usage: take <item> [qty]"
            })
            return

        map_name = player.position["map_name"]
        room_id = player.position["room"]

        # Get current room object
        room = game.world.get(map_name)
        if not room:
            send_json_to(conn, {
                "type": "error",
                "message": "Current map not found."
            })
            return

        room_obj = room.get_room(room_id)
        if not room_obj:
            send_json_to(conn, {
                "type": "error",
                "message": "Current room not found."
            })
            return

        # Resolve key in room items (support both key and display name)
        key = room_obj._resolve_key(item_name)
        if not key:
            send_json_to(conn, {
                "type": "take",
                "ok": False,
                "message": f"'{item_name}' is not in this room."
            })
            return

        # Get display_name and description before removing item
        display_name, _, description = room_obj.items[key]

        # Attempt to remove the specified quantity from the room
        success = room_obj.remove_item(key, qty)
        if not success:
            send_json_to(conn, {
                "type": "take",
                "ok": False,
                "message": f"Cannot take '{item_name}' x{qty} from the room."
            })
            return

        # Add item to player's inventory
        player.add_item(key, display_name, qty, description)

        # Notify all players in room about the pickup
        broadcast_chat_in_room(
            f"{player.name} picks up {display_name} x{qty}",
            room_obj.players,
            sender=player
        )

        # Respond to the player
        send_json_to(conn, {
            "type": "take",
            "ok": True,
            "item": {
                "key": key,
                "name": display_name,
                "quantity": qty,
            }
        })

    # Examine item from inventory
    if command == "examine":
        item_name = str(payload.get("item", "")).strip()

        if not item_name:
            send_json_to(conn, {
                "type": "system",
                "message": "Usage: examine <item>"
            })
            return

        key = player._resolve_key(item_name)
        if not key:
            send_json_to(conn, {
                "type": "system",
                "message": f"'{item_name}' not found in your inventory."
            })
            return

        name, qty, desc = player.inventory[key]

        send_json_to(conn, {
            "type": "examine",
            "item": {
                "key": key,
                "name": name,
                "quantity": qty,
                "description": desc
            }
        })
        return

    if command == "drop":
        # Drop item from inventory into current room
        qty, item_name = _parse_name_qty_from_payload(payload)

        if not item_name:
            send_json_to(conn, {
                "type": "error",
                "message": "Usage: drop <item> [qty]"
            })
            return

        if not hasattr(game, "add_room_item"):
            send_json_to(conn, {
                "type": "error",
                "message": "Room items not available yet on server."
            })
            return

        if not player.has_item(item_name, qty):
            send_json_to(conn, {
                "type": "drop",
                "ok": False,
                "message": f"You don't have '{item_name}' x{qty}."
            })
            return

        resolved_key = player._resolve_key(item_name)
        display_name, have, description = player.inventory[resolved_key]

        if not player.remove_item(item_name, qty):
            send_json_to(conn, {
                "type": "drop",
                "ok": False,
                "message": "Failed to update ypur inventory."
            })
            return

        map_name = player.position["map_name"]
        room_id = player.position["room"]

        game.add_room_item(
            map_name,
            room_id,
            resolved_key,
            display_name,
            qty,
            description
        )

        broadcast_chat(
            f"{player.name} drops {display_name} x{qty}",
            sender=player
        )

        send_json_to(conn, {
            "type": "drop",
            "ok": True,
            "item": {
                "key": resolved_key,
                "name": display_name,
                "quantity": qty,
            }
        })

    if command == "look":
        # Show current room information and floor items
        map_name = player.position["map_name"]
        room_id = player.position["room"]

        items = game.list_room_items(map_name, room_id)
        npcs = game.list_npcs_in_room(map_name, room_id)

        send_json_to(conn, {
            "type": "look",
            "message": f"You are in {map_name}/{room_id}",
            "room": {"map": map_name, "id": room_id},
            "floor": items,
            "npcs": [npc.name for npc in npcs]
        })
        return

    # Command talk
    if command == "talk":
        target = str(payload.get("target", "")).strip()

        if not target:
            send_json_to(conn, {
                "type": "system",
                "message": "Usage: talk <npc>"
            })
            return

        map_name = player.position["map_name"]
        room_id = player.position["room"]

        npc = game.find_npc_in_room(map_name, room_id, target)

        if not npc:
            send_json_to(conn, {
                "type": "system",
                "message": f"There is no '{target}' here."
            })
            return

        response = npc.talk()

        send_json_to(conn, {
            "type": "npc_talk",
            "npc": npc.name,
            "message": response
        })
        return

    if command == "help":
        # Return list of available commands
        send_json_to(conn, {
            "type": "help",
            "commands": [
                "help",
                "inv",
                "examine <item>",
                "look",
                "take <item> [qty]",
                "drop <item> [qty]",
                "yell <message>",
            ]
        })
        return
