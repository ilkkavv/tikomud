from tikomud.server.game.room import Room
import os
import json

class Map:
    def __init__(self, path: str):
        base_dir = os.path.dirname(__file__)
        self.rooms_path = os.path.join(base_dir, path)
        self.rooms = []
        self.load_rooms()

    def load_rooms(self) -> None:
        for filename in os.listdir(self.rooms_path):
            if not filename.endswith(".json"):
                continue

            filepath = os.path.join(self.rooms_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            room_id = filename.replace(".json", "")
            room = Room(
                room_id=room_id,
                name=data["name"],
                description=data.get("description", ""),
                exits=data.get("exits", {}),
                coordinates=data.get("coordinates", {})
            )
            self.rooms.append(room)

    def get_room(self, room_id: str) -> Room | None:
        for room in self.rooms:
            if room.id == room_id:
                return room
        return None