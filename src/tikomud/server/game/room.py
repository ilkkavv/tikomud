from tikomud.server.game.player import Player
import threading

class Room:
    def __init__(self, room_id, name = "", description = "", items=None, exits=None):
        if exits is None:
            exits = {}
        if items is None:
            items = []

        self.id = room_id
        self.name = name
        self.description = description
        self.items = items
        self.exits = exits
        self.players = []

        self.players_lock = threading.Lock()

    def add_player(self, player: Player):
        with self.players_lock:
            self.players.append(player)

    def remove_player(self, player: Player):
        with self.players_lock:
            if player in self.players:
                self.players.remove(player)
