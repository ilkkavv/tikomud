from tikomud.server.game.player import Player
from tikomud.server.game.map import Map
import threading

class Game:
    def __init__(self):
        self.world = {"overworld": Map("rooms/overworld")}
        self.players = []

        self.room_items = {}

        self.game_lock = threading.Lock()

    def add_player(self, new_player: Player) -> None:
        with self.game_lock:
            self.players.append(new_player)

    def remove_player(self, player: Player) -> None:
        with self.game_lock:
            if player in self.players:
                self.players.remove(player)

    def move_player(self, player: Player, direction: str):
        current_map_name = player.position["map_name"]
        current_room_id = player.position["room"]

        game_map = self.world.get(current_map_name)
        if not game_map:
            return False, "Current map not found."

        current_room = game_map.get_room(current_room_id)
        if not current_room:
            return False, "Current room not found."

        if direction not in current_room.exits:
            return False, f"You cannot go {direction}."

        target = current_room.exits[direction]
        target_map_name = target["map"]
        target_room_id = target["room"]

        target_map = self.world.get(target_map_name)
        if not target_map:
            return False, "Target map not found."

        target_room = target_map.get_room(target_room_id)
        if not target_room:
            return False, "Target room not found."

        current_room.remove_player(player)
        target_room.add_player(player)
        player.set_position(target_map_name, target_room_id)

        return True, f"You move {direction}.\n{target_room.description}"