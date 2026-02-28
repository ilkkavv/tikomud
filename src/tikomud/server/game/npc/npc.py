# Class for various NPC interactions
# First implementation will focus on dialogue only

# Later can implement
#   - Combat
#   - Trading
#   - etc

class NPC:
    def __init__(self, name: str, room):
        self.name = name
        self.room = room

    def act(self, game):
        pass  # AI logic here
