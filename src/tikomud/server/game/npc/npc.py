# Class for various NPC interactions
# First implementation will focus on dialogue only

# Later can implement
#   - Combat
#   - Trading
#   - etc

class NPC:
    def __init__(self, npc_id: str, name: str, description: str, dialogue: list[str]):
        self.id = npc_id
        self.name = name
        self.description = description
        self.dialogue = dialogue

        # same structure as player
        self.position = {}

    def set_position(self, map_name: str, room_id: str):
        self.position["map_name"] = map_name
        self.position["room"] = room_id

    def talk(self):
        if not self.dialogue:
            return "They have nothing to say."
        return self.dialogue[0]  # simplest version
