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

    return None, f"Unknown command: {cmd}"

def send_validated(connection, user_input: str) -> Optional[str]:
    packet, local_msg = validate(user_input)

    if local_msg is not None:
        return local_msg

    if packet is None:
        return None

    connection.send_json(packet)
    return None
