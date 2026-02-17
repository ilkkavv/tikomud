from player import Player

class Game:
    def __init__(self, worlds: []):
        self.world = worlds
        self.players = []

    def add_player(self, new_player: Player) -> None:
        self.players.append(new_player)
