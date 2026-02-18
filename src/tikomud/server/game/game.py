from tikomud.server.game.player import Player
from tikomud.server.game.map import Map
import threading

class Game:
    def __init__(self):
        self.world = {"overworld": Map("rooms/overworld")}
        self.players = []

        self.game_lock = threading.Lock()

    def add_player(self, new_player: Player) -> None:
        with self.game_lock:
            self.players.append(new_player)

    def remove_player(self, player: Player) -> None:
        with self.game_lock:
            if player in self.players:
                self.players.remove(player)
