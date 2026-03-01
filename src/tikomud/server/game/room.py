from tikomud.server.game.player import Player
import threading

class Room:
    def __init__(self, room_id, name = "", description = "", exits=None, coordinates=None):
        if exits is None:
            exits = {}
        if coordinates is None:
            coordinates = {}

        self.id = room_id
        self.name = name
        self.description = description

        # Runtime storage for room items
        self.items = {}

        self.exits = exits
        self.players = []
        self.coordinates = coordinates

        # Locks for thread-safe access
        self.players_lock = threading.Lock()
        self.items_lock = threading.Lock()

    def add_player(self, player: Player):
        with self.players_lock:
            self.players.append(player)

    def remove_player(self, player: Player):
        with self.players_lock:
            if player in self.players:
                self.players.remove(player)

    ## Add an item to the room or increase quantity if already present
    def add_item(self, key: str, display_name: str, qty: int = 1, description: str = ""):
        key = (key or "").strip().lower()
        if not key or qty <= 0:
            return

        with self.items_lock:
            if key in self.items:
                name0, qty0, desc0 = self.items[key]
                self.items[key] = (name0, qty0 + qty, desc0 or description)
            else:
                self.items[key] = (display_name, qty, description)

    # Remove specified quantity of an item from the room
    def remove_item(self, key_or_name: str, qty: int = 1) -> bool:
        key = self._resolve_key(key_or_name)
        if not key or qty <= 0:
            return False

        with self.items_lock:
            name, qty_have, desc = self.items[key]
            if qty_have < qty:
                return False

            new_qty = qty_have - qty
            if new_qty == 0:
                del self.items[key]
            else:
                self.items[key] = (name, new_qty, desc)
        return True

    # Return list of item display strings for the room
    def list_items(self):
        with self.items_lock:
            if not self.items:
                return ["(nothing)"]
            return [f"{name} x{qty}" for _k, (name, qty, _desc) in sorted(self.items.items())]

    # Resolve an item key by exact key match or display name (case-insensitive)
    def _resolve_key(self, key_or_name: str):
        query = (key_or_name or "").strip().lower()
        if not query:
            return None

        with self.items_lock:
            if query in self.items:
                return query

            matches = [
                key for key, (display_name, _qty, _desc) in self.items.items()
                if (display_name or "").strip().lower() == query
            ]
            if len(matches) == 1:
                return matches[0]
        return None

    def get_item_info(self, key: str):
        with self.items_lock:
            return self.items.get(key)
