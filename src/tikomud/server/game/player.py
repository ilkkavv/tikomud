class Player:
    def __init__(self, name):
        self.name = name
        self.position = {
            "map_name": "overworld",
            "room": "room1"
        }

        # NEW: Player inventory structure
        self.inventory = {}

    def set_position(self, map_name: str, room_id: str):
        self.position["map_name"] = map_name
        self.position["room"] = room_id

    def add_item(self, key: str, name: str, qty: int = 1, desc: str = ""):
        key = key.lower().strip()

        if key in self.inventory:
            current_name, current_qty, current_desc = self.inventory[key]
            self.inventory[key] = (current_name, current_qty + qty, current_desc or desc)
        else:
            self.inventory[key] = (name, qty, desc)

    def list_inventory(self):
        if not self.inventory:
            return ["(empty)"]

        lines = []
        for key, (name, qty, desc) in self.inventory.items():
            lines.append(f"{name} x{qty}")
        return lines

    def _resolve_key(self, key_or_name: str):
        query = key_or_name.strip().lower()
        if not query:
            return None

        if query in self.inventory:
            return query

        matches = [
            key for key, (display_name, _qty, _desc) in self.inventory.items()
            if display_name.lower() == query
        ]
        if len(matches) == 1:
            return matches[0]

        return None

    def has_item(self, key_or_name, qty = 1):
        resolved_key = self._resolve_key(key_or_name)
        if not resolved_key:
            return False

        _name, qty_have, _desc = self.inventory[resolved_key]
        return qty_have >= max(1, qty)

    def remove_item(self, key_or_name, qty = 1):
        resolved_key = self._resolve_key(key_or_name)
        if not resolved_key or qty <= 0:
            return False

        name, qty_have, desc = self.inventory[resolved_key]
        if qty_have < qty:
            return False

        new_qty = qty_have - qty
        if new_qty == 0:
            del self.inventory[resolved_key]
            return True
        else:
            self.inventory[resolved_key] = (name, new_qty, desc)
            return True