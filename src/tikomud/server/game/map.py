from tikomud.server.game.room import Room
import os
import json

class Map:
    def __init__(self, path):

        self.rooms = []
        self.load_rooms(path)

    def load_rooms(self, path):
        rooms_path = path

        for filename in os.listdir(rooms_path):
            if filename.endswith(".json"):
                filepath = os.path.join(rooms_path, filename)

                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    room_id = filename.replace(".json", "")

                    room = Room(
                        room_id=room_id,
                        name=data["name"],
                        description=data.get("description", ""),
                        items=data.get("items", []),
                        exits=data.get("exits", {}),
                        coordinates=data.get("coordinates", {})
                    )

                    self.rooms.append(room)
