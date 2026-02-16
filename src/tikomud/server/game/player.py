class Player:
    def __init__(self, name):
        self.name = name
        self.position = {
            "map": "overworld",
            "x": 0,
            "y": 0
        }

    def move(self, direction: str):
        direction = direction.lower()

        if direction == "north":
            self.position["y"] += 1
        elif direction == "south":
            self.position["y"] -= 1
        elif direction == "east":
            self.position["x"] += 1
        elif direction == "west":
            self.position["y"] -= 1
        else:
            return f"Unknown direction: {direction}"

        return f"{self.name} moved {direction}. New position: {self.position}"