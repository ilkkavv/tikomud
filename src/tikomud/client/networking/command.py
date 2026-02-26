import json
from typing import Optional, Dict, Any, Tuple

Packet = Dict[str, Any]

def validate(user_input: str) -> Tuple[Optional[Packet], Optional[str]]:
    parts = user_input.strip().split()
    if not parts:
        return None, None

    cmd = parts[0].lower()

    if cmd == "yell":
        if len(parts) < 2:
            return None, "Usage: yell <message>"

        message = " ".join(parts[1:]).strip()
        if not message:
            return None, "Usage: yell <message>"

        return {
            "type": "command",
            "command": "yell",
            "payload": {"message": message},
        }, None

    if cmd == "say":
        if len(parts) < 2:
            return None, "Usage: say <message>"

        message = " ".join(parts[1:]).strip()
        if not message:
            return None, "Usage: say <message>"

        return {
            "type": "command",
            "command": "say",
            "payload": {"message": message},
        }, None

    if cmd in ("inv", "inventory"):
        if len(parts) == 1:
            return {
                "type": "command",
                "command": "inv",
                "payload": {},
            }, None

        return None, "Usage: inv or inventory"

    if cmd in ("m", "move"):
        payload = ""
        if len(parts) == 2:
            if parts[1] in ("n", "north"):
                payload = "north"
            elif parts[1] in ("e", "east"):
                payload = "east"
            elif parts[1] in ("s", "south"):
                payload = "south"
            elif parts[1] in ("w", "west"):
                payload = "west"
            elif parts[1] in ("u", "up"):
                payload = "up"
            elif parts[1] in ("d", "down"):
                payload = "down"
            else:
                return None, "Usage: move [direction]"

            return {
                "type": "command",
                "command": "move",
                "payload": {"dir": payload},
            }, None

        return None, "Usage: move [direction]"

    return None, f"Unknown command: {cmd}"

def send_validated(connection, user_input: str) -> Optional[str]:
    packet, local_msg = validate(user_input)

    if local_msg is not None:
        return local_msg

    if packet is None:
        return None

    connection.send_json(packet)
    return None
