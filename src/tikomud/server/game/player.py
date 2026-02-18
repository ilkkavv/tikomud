class Player:
    def __init__(self, name):
        self.name = name
        self.position = {
            "map_name": "overworld",
            "room": "room1"
        }

    def set_position(self, map_name: str, room_id: str):
        self.position["map_name"] = map_name
        self.position["room"] = room_id
