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

    def add_item(self, key: str, name: str, qty: int = 1):
        key = key.lower().strip()

        if key in self.inventory:
            current_name, current_qty = self.inventory[key]
            self.inventory[key] = (current_name, current_qty + qty)
        else:
            self.inventory[key] = (name, qty)
