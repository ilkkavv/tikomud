from tikomud.server.game.player import Player
from tikomud.server.game.map import Map
from tikomud.server.game.npc import NPC
import json
import os
import threading

class Game:
    def __init__(self):
        self.world = {"overworld": Map("rooms/overworld")}
        self.players = []
        self.npcs = []

        self.game_lock = threading.Lock()
        self.load_npcs()

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

    # Helper function to find npcs
    def find_npc_in_room(self, map_name: str, room_id: str, name: str):
        name = name.strip().lower()

        for npc in self.npcs:
            if (
                npc.position["map_name"] == map_name and
                npc.position["room"] == room_id and
                npc.name.lower() == name
            ):
                return npc

        return None

    # Function to list npcs inside current room
    def list_npcs_in_room(self, map_name: str, room_id: str):
        return [
            npc for npc in self.npcs
            if npc.position["map_name"] == map_name
            and npc.position["room"] == room_id
        ]

    def load_npcs(self):
        npc_folder = os.path.join(os.path.dirname(__file__), "npcs")

        if not os.path.isdir(npc_folder):
            return

        for filename in os.listdir(npc_folder):
            if not filename.endswith(".json"):
                continue

            with open(os.path.join(npc_folder, filename)) as f:
                data = json.load(f)

            npc = NPC(
                data["id"],
                data["name"],
                data.get("description", ""),
                data.get("dialogue", [])
            )

            spawn = data["spawn"]
            npc.set_position(spawn["map_name"], spawn["room"])

            self.npcs.append(npc)
